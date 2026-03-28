from __future__ import annotations

from datetime import datetime, timedelta

import pyotp
from SmartApi import SmartConnect

from scanner.brokers.base import BrokerClient
from scanner.config import ScannerConfig, SmartApiCredentials, SymbolConfig
from scanner.models import Candle, SymbolSnapshot


class SmartApiBroker(BrokerClient):
    def __init__(self, credentials: SmartApiCredentials, scanner_config: ScannerConfig) -> None:
        self.credentials = credentials
        self.scanner_config = scanner_config
        self.client = SmartConnect(api_key=credentials.api_key)
        self._refresh_token: str | None = None

    def authenticate(self) -> None:
        totp = pyotp.TOTP(self.credentials.totp_secret).now()
        login_data = self.client.generateSession(
            self.credentials.client_id,
            self.credentials.password,
            totp,
        )
        if not login_data.get("status"):
            raise RuntimeError(f"SmartAPI login failed: {login_data}")

        payload = login_data["data"]
        self._refresh_token = payload["refreshToken"]
        self.client.generateToken(self._refresh_token)

    def ensure_session(self) -> None:
        if not self._refresh_token:
            self.authenticate()
            return

        try:
            self.client.getProfile(self._refresh_token)
        except Exception:
            token_data = self.client.generateToken(self._refresh_token)
            if not token_data.get("status"):
                self.authenticate()

    def fetch_snapshots(self) -> list[SymbolSnapshot]:
        self.ensure_session()
        snapshots: list[SymbolSnapshot] = []
        for symbol in self.scanner_config.symbols:
            snapshots.append(self._build_snapshot(symbol))
        return snapshots

    def _build_snapshot(self, symbol: SymbolConfig) -> SymbolSnapshot:
        ltp_payload = self.client.ltpData(symbol.exchange, symbol.symbol, symbol.token)
        if not ltp_payload.get("status"):
            raise RuntimeError(f"LTP fetch failed for {symbol.symbol}: {ltp_payload}")

        ltp_data = ltp_payload["data"]
        latest_candles = self._fetch_candles(symbol, points=3)
        if len(latest_candles) < 2:
            raise RuntimeError(f"Insufficient candle data for {symbol.symbol}")

        current = latest_candles[-1]
        previous = latest_candles[-2]
        opening = self._fetch_opening_candle(symbol)
        vwap = self._calculate_vwap(latest_candles)

        return SymbolSnapshot(
            symbol=symbol.symbol,
            ltp=float(ltp_data["ltp"]),
            open_price=current.open,
            high=current.high,
            low=current.low,
            close=current.close,
            volume=current.volume,
            previous_volume=previous.volume,
            vwap=vwap,
            opening_high=opening.high,
            opening_low=opening.low,
        )

    def _fetch_opening_candle(self, symbol: SymbolConfig) -> Candle:
        candles = self._fetch_candles(symbol, points=60)
        trade_day = datetime.now().date()
        same_day = [candle for candle in candles if candle.timestamp.date() == trade_day]
        if not same_day:
            return candles[-1]
        return min(same_day, key=lambda x: x.timestamp)

    def _fetch_candles(self, symbol: SymbolConfig, points: int) -> list[Candle]:
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=max(points, 5) * self.scanner_config.timeframe_minutes)

        payload = {
            "exchange": symbol.exchange,
            "symboltoken": symbol.token,
            "interval": f"ONE_MINUTE" if self.scanner_config.timeframe_minutes == 1 else "FIVE_MINUTE",
            "fromdate": start_time.strftime("%Y-%m-%d %H:%M"),
            "todate": end_time.strftime("%Y-%m-%d %H:%M"),
        }
        response = self.client.getCandleData(payload)
        if not response.get("status"):
            raise RuntimeError(f"Candle fetch failed for {symbol.symbol}: {response}")

        candles: list[Candle] = []
        for row in response["data"]:
            candles.append(
                Candle(
                    timestamp=datetime.fromisoformat(row[0].replace("Z", "+00:00")).replace(tzinfo=None),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=float(row[5]),
                )
            )
        return candles[-points:]

    @staticmethod
    def _calculate_vwap(candles: list[Candle]) -> float | None:
        total_volume = sum(c.volume for c in candles)
        if total_volume <= 0:
            return None
        total_price_volume = sum(((c.high + c.low + c.close) / 3) * c.volume for c in candles)
        return total_price_volume / total_volume
