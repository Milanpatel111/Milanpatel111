from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


class SignalLogger:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self._ensure_header()

    def _ensure_header(self) -> None:
        if self.file_path.exists():
            return
        with self.file_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow(["timestamp", "symbol", "signal", "price"])

    def append(self, symbol: str, signal: str, price: float) -> None:
        with self.file_path.open("a", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow([datetime.now().isoformat(), symbol, signal, f"{price:.2f}"])
