from __future__ import annotations

import logging

from scanner.brokers.smartapi import SmartApiBroker
from scanner.brokers.upstox import UpstoxBroker
from scanner.config import (
    load_env,
    load_scanner_config,
    load_smartapi_credentials,
    load_telegram_config,
    load_upstox_credentials,
)
from scanner.notifier import TelegramNotifier
from scanner.scanner import MarketScanner
from scanner.signal_logger import SignalLogger
from scanner.strategy import BreakoutStrategy


def build_broker(scanner_config):
    broker_name = scanner_config.broker.lower()
    if broker_name == "smartapi":
        credentials = load_smartapi_credentials()
        return SmartApiBroker(credentials, scanner_config)
    if broker_name == "upstox":
        credentials = load_upstox_credentials()
        return UpstoxBroker(credentials, scanner_config)
    raise ValueError(f"Unsupported broker: {scanner_config.broker}")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    load_env()
    scanner_config = load_scanner_config("config.json")
    telegram_config = load_telegram_config()

    broker = build_broker(scanner_config)
    strategy = BreakoutStrategy(use_vwap_filter=scanner_config.use_vwap_filter)
    notifier = TelegramNotifier(telegram_config)
    signal_logger = SignalLogger(scanner_config.log_file)

    scanner = MarketScanner(
        broker=broker,
        strategy=strategy,
        notifier=notifier,
        signal_logger=signal_logger,
        scan_interval_seconds=scanner_config.scan_interval_seconds,
    )
    scanner.run_forever()


if __name__ == "__main__":
    main()
