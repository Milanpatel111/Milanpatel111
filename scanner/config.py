from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class SymbolConfig:
    symbol: str
    exchange: str
    token: str


@dataclass(slots=True)
class ScannerConfig:
    broker: str = "smartapi"
    scan_interval_seconds: int = 10
    timeframe_minutes: int = 1
    use_vwap_filter: bool = True
    symbols: list[SymbolConfig] = field(default_factory=list)
    log_file: str = "signals.csv"


@dataclass(slots=True)
class SmartApiCredentials:
    api_key: str
    client_id: str
    password: str
    totp_secret: str


@dataclass(slots=True)
class UpstoxCredentials:
    access_token: str


@dataclass(slots=True)
class TelegramConfig:
    bot_token: str
    chat_id: str


def load_env() -> None:
    load_dotenv()


def load_scanner_config(path: str = "config.json") -> ScannerConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    symbols = [SymbolConfig(**item) for item in raw.get("symbols", [])]
    return ScannerConfig(
        broker=raw.get("broker", "smartapi"),
        scan_interval_seconds=int(raw.get("scan_interval_seconds", 10)),
        timeframe_minutes=int(raw.get("timeframe_minutes", 1)),
        use_vwap_filter=bool(raw.get("use_vwap_filter", True)),
        symbols=symbols,
        log_file=raw.get("log_file", "signals.csv"),
    )


def load_smartapi_credentials() -> SmartApiCredentials:
    return SmartApiCredentials(
        api_key=os.environ["SMARTAPI_API_KEY"],
        client_id=os.environ["SMARTAPI_CLIENT_ID"],
        password=os.environ["SMARTAPI_PASSWORD"],
        totp_secret=os.environ["SMARTAPI_TOTP_SECRET"],
    )


def load_upstox_credentials() -> UpstoxCredentials:
    return UpstoxCredentials(access_token=os.environ["UPSTOX_ACCESS_TOKEN"])


def load_telegram_config() -> TelegramConfig:
    return TelegramConfig(
        bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        chat_id=os.environ["TELEGRAM_CHAT_ID"],
    )
