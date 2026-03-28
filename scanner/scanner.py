from __future__ import annotations

import logging
import time

from scanner.brokers.base import BrokerClient
from scanner.notifier import TelegramNotifier
from scanner.signal_logger import SignalLogger
from scanner.strategy import BreakoutStrategy


class MarketScanner:
    def __init__(
        self,
        broker: BrokerClient,
        strategy: BreakoutStrategy,
        notifier: TelegramNotifier,
        signal_logger: SignalLogger,
        scan_interval_seconds: int,
    ) -> None:
        self.broker = broker
        self.strategy = strategy
        self.notifier = notifier
        self.signal_logger = signal_logger
        self.scan_interval_seconds = scan_interval_seconds
        self._last_signal_sent: dict[str, str] = {}

    def run_forever(self) -> None:
        logging.info("Starting market scanner...")
        self.broker.authenticate()

        while True:
            try:
                snapshots = self.broker.fetch_snapshots()
                for snapshot in snapshots:
                    signal = self.strategy.generate_signal(snapshot)
                    if not signal:
                        continue

                    if self._last_signal_sent.get(snapshot.symbol) == signal:
                        logging.info("Duplicate signal skipped for %s (%s)", snapshot.symbol, signal)
                        continue

                    self.notifier.send_signal(signal, snapshot.symbol, snapshot.ltp)
                    self.signal_logger.append(snapshot.symbol, signal, snapshot.ltp)
                    self._last_signal_sent[snapshot.symbol] = signal
                    logging.info("%s SIGNAL: %s @ %.2f", signal, snapshot.symbol, snapshot.ltp)

            except Exception as exc:
                logging.exception("Scanner error: %s", exc)

            time.sleep(self.scan_interval_seconds)
