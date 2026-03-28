from __future__ import annotations

from scanner.models import SymbolSnapshot


class BreakoutStrategy:
    def __init__(self, use_vwap_filter: bool = True) -> None:
        self.use_vwap_filter = use_vwap_filter

    def generate_signal(self, snapshot: SymbolSnapshot) -> str | None:
        volume_spike = snapshot.volume > snapshot.previous_volume

        if snapshot.ltp > snapshot.opening_high and volume_spike:
            if self._passes_vwap(snapshot, direction="BUY"):
                return "BUY"

        if snapshot.ltp < snapshot.opening_low and volume_spike:
            if self._passes_vwap(snapshot, direction="SELL"):
                return "SELL"

        return None

    def _passes_vwap(self, snapshot: SymbolSnapshot, direction: str) -> bool:
        if not self.use_vwap_filter or snapshot.vwap is None:
            return True
        if direction == "BUY":
            return snapshot.ltp > snapshot.vwap
        return snapshot.ltp < snapshot.vwap
