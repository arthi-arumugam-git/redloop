"""The Day-1 search scaffold evaluates isolated runs and keeps the best."""

import json

import pytest

from redloop.attacker.base import Attacker
from redloop.attacker.loop import attack_loop
from redloop.attacker.seed_attacker import SeedAttacker
from redloop.runner import load_scenario


def test_seed_payload_and_mutations_are_static_and_reproducible():
    attacker = SeedAttacker()
    scenario = load_scenario("email_exfil")
    seeds = attacker.seeds(scenario)
    assert scenario["seed_payload"] in seeds
    mutations = attacker.mutate(seeds[0])
    assert mutations == attacker.mutate(seeds[0])
    assert len(mutations) >= 2
    assert len(set(mutations)) == len(mutations)
    assert all(seeds[0] in payload and payload != seeds[0] for payload in mutations)


def test_search_mutates_best_and_keeps_earliest_equal_score(tmp_path):
    path = tmp_path / "trials.jsonl"
    scenario = load_scenario("email_exfil")
    best = attack_loop(scenario, "naive", rounds=1, results_path=path)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows) == 1 + len(SeedAttacker().mutate(scenario["seed_payload"]))
    assert all(row["status"] == "red" for row in rows)
    assert best == rows[0]
    assert best["score"] == max(row["score"] for row in rows)


def test_search_improves_on_benign_seed_and_deduplicates_candidates(tmp_path):
    seed = load_scenario("email_exfil")["seed_payload"]

    class ImprovingAttacker(Attacker):
        def __init__(self):
            self.inputs = []

        def seeds(self, scenario):
            return ["", ""]

        def mutate(self, payload):
            self.inputs.append(payload)
            return [seed, seed]

    attacker = ImprovingAttacker()
    path = tmp_path / "trials.jsonl"
    best = attack_loop("email_exfil", "naive", attacker, rounds=2, results_path=path)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert [row["status"] for row in rows] == ["green", "red"]
    assert attacker.inputs == ["", seed]
    assert best == rows[-1]


def test_zero_mutation_rounds_still_evaluates_seed():
    best = attack_loop("github_destructive", "guarded", rounds=0, results_path=None)
    assert best["status"] == "green"
    assert best["score"] == 0
    assert best["payload"] == load_scenario("github_destructive")["seed_payload"]


def test_negative_round_count_is_rejected():
    with pytest.raises(ValueError, match="rounds"):
        attack_loop("email_exfil", "naive", rounds=-1, results_path=None)


def test_skipped_target_is_not_treated_as_a_successful_defense(monkeypatch, tmp_path):
    for name in ("LLAMA_BASE_URL", "LLAMA_API_KEY", "LLAMA_MODEL"):
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / "trials.jsonl"
    with pytest.raises(RuntimeError, match="No completed attack trials"):
        attack_loop("email_exfil", "llama", results_path=path)
    assert json.loads(path.read_text())["status"] == "skipped"
