"""Day-1 mutate -> run -> score -> keep-best scaffold."""

from pathlib import Path
from typing import Any

from redloop.runner import DEFAULT_RESULTS, load_scenario, run_scenario
from redloop.targets import Agent

from .base import Attacker
from .seed_attacker import SeedAttacker


def attack_loop(
    scenario: str | Path | dict[str, Any],
    agent: str | Agent,
    attacker: Attacker | None = None,
    *,
    rounds: int = 1,
    results_path: str | Path | None = DEFAULT_RESULTS,
) -> dict[str, Any]:
    if rounds < 0:
        raise ValueError("rounds must be nonnegative")
    fixture = load_scenario(scenario)
    source = attacker if attacker is not None else SeedAttacker()
    candidates = source.seeds(fixture)
    seen: set[str] = set()
    best = None
    for generation in range(rounds + 1):
        fresh = [payload for payload in candidates if payload not in seen]
        if not fresh:
            break
        for payload in fresh:
            if payload in seen:
                continue
            seen.add(payload)
            row = run_scenario(fixture, agent, payload, results_path=results_path)
            if row["status"] not in ("red", "green"):
                continue
            if best is None or row["score"] > best["score"]:
                best = row
        if best is None:
            break
        if generation < rounds:
            candidates = source.mutate(best["payload"])
    if best is None:
        raise RuntimeError("No completed attack trials; inspect skipped/error results")
    # TODO D3-5: model-driven mutations, richer fitness, search budgets and
    # lineage/checkpoints. This scaffold intentionally keeps the earliest tie.
    return best
