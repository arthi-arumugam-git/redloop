from abc import ABC, abstractmethod
from typing import Any


class Attacker(ABC):
    @abstractmethod
    def seeds(self, scenario: dict[str, Any]) -> list[str]:
        """Return initial payloads for this scenario."""

    @abstractmethod
    def mutate(self, payload: str) -> list[str]:
        """Propose payload variations without changing the trusted task."""
