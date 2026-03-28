from __future__ import annotations

from datetime import datetime

import requests

from scanner.brokers.base import BrokerClient
from scanner.config import ScannerConfig, UpstoxCredentials
from scanner.models import SymbolSnapshot


class UpstoxBroker(BrokerClient):
    BASE_URL = "https://api.upstox.com/v2"

    def __init__(self, credentials: UpstoxCredentials, scanner_config: ScannerConfig) -> None:
        self.credentials = credentials
        self.scanner_config = scanner_config

    def authenticate(self) -> None:
        if not self.credentials.access_token:
            raise RuntimeError("UPSTOX_ACCESS_TOKEN is missing.")

    def ensure_session(self) -> None:
        self.authenticate()

    def fetch_snapshots(self) -> list[SymbolSnapshot]:
        self.ensure_session()
        snapshots: list[SymbolSnapshot] = []
        for symbol in self.scanner_config.symbols:
            instrument_key = f"{symbol.exchange}|{symbol.symbol}"
            quote = self._fetch_quote(instrument_key)
            candle_data = self._fetch_intraday_candles(instrument_key)
            if len(candle_data) < 2:
                continue

            current = candle_data[-1]
            previous = candle_data[-2]
            opening = next((row for row in candle_data if row[0][:10] == datetime.now().strftime("%Y-%m-%d")), candle_data[0])

            snapshots.append(
                SymbolSnapshot(
                    symbol=symbol.symbol,
                    ltp=float(quote["last_price"]),
                    open_price=float(current[1]),
                    high=float(current[2]),
                    low=float(current[3]),
                    close=float(current[4]),
                    volume=float(current[5]),
                    previous_volume=float(previous[5]),
                    vwap=float(current[6]) if len(current) > 6 else None,
                    opening_high=float(opening[2]),
                    opening_low=float(opening[3]),
                )
            )
        return snapshots

    def _fetch_quote(self, instrument_key: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}/market-quote/ltp",
            params={"instrument_key": instrument_key},
            headers=self._headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        if instrument_key not in data:
            raise RuntimeError(f"No quote data for {instrument_key}")
        return data[instrument_key]

    def _fetch_intraday_candles(self, instrument_key: str) -> list[list]:
        response = requests.get(
            f"{self.BASE_URL}/historical-candle/intraday/{instrument_key}/1minute",
            headers=self._headers,
            timeout=15,
        )
        response.raise_for_status()
        candles = response.json().get("data", {}).get("candles", [])
        return candles[-10:]

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Accept": "application/json",
        }
