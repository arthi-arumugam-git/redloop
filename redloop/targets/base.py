"""Common target-agent contract."""

from abc import ABC, abstractmethod
from typing import Any

from redloop.sandbox import Sandbox


class AgentUnavailable(RuntimeError):
    """The optional target is not configured; report a skipped experiment."""


class Agent(ABC):
    name: str

    @abstractmethod
    def run(self, sandbox: Sandbox, scenario: dict[str, Any]) -> str:
        """Perform the trusted task using the supplied isolated sandbox."""
