"""Target factory; optional network targets are loaded only on request."""

from .base import Agent, AgentUnavailable
from .rule_agent import GuardedAgent, RuleAgent


def make_agent(name: str) -> Agent:
    if name == "naive":
        return RuleAgent()
    if name == "guarded":
        return GuardedAgent()
    if name == "llama":
        from .llama_agent import LlamaAgent

        return LlamaAgent()
    raise ValueError(f"Unknown agent: {name}")


__all__ = ["Agent", "AgentUnavailable", "RuleAgent", "GuardedAgent", "make_agent"]
