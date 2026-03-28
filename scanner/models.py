from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class SymbolSnapshot:
    symbol: str
    ltp: float
    open_price: float
    high: float
    low: float
    close: float
    volume: float
    previous_volume: float
    vwap: float | None
    opening_high: float
    opening_low: float
