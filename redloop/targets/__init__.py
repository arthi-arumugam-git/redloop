"""Target factory; optional network targets are loaded only on request."""

from .base import Agent, AgentUnavailable
from .rule_agent import GuardedAgent, RuleAgent

AGENT_NAMES = ("naive", "guarded", "spotlight-only", "allowlist-only", "llama", "llama-guarded")


def make_agent(name: str) -> Agent:
    if name == "naive":
        return RuleAgent()
    if name == "guarded":
        return GuardedAgent()
    if name == "spotlight-only":
        return RuleAgent(spotlight=True, allowlist=False, name=name)
    if name == "allowlist-only":
        return RuleAgent(spotlight=False, allowlist=True, name=name)
    if name == "llama":
        from .llama_agent import LlamaAgent

        return LlamaAgent()
    if name == "llama-guarded":
        from .llama_agent import LlamaAgent

        return LlamaAgent(defended=True)
    raise ValueError(f"Unknown agent: {name}")


__all__ = ["AGENT_NAMES", "Agent", "AgentUnavailable", "RuleAgent", "GuardedAgent", "make_agent"]
