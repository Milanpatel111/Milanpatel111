from __future__ import annotations

from abc import ABC, abstractmethod

from scanner.models import SymbolSnapshot


class BrokerClient(ABC):
    @abstractmethod
    def authenticate(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def ensure_session(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def fetch_snapshots(self) -> list[SymbolSnapshot]:
        raise NotImplementedError
