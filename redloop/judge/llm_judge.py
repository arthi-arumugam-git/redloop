"""Extension seam for a later semantic judge; never silently returns a pass."""

from abc import ABC, abstractmethod
from typing import Any

from redloop.policy import Policy, Violation


class LLMJudge(ABC):
    @abstractmethod
    def score(self, action_log: list[dict[str, Any]], policy: Policy) -> list[Violation]:
        """TODO D3-5: add semantic evidence and calibrate against the rule judge."""
        raise NotImplementedError
