"""Fresh sandbox runs demonstrate the attacker-to-tool trust boundary."""

import copy
import json

import pytest

from redloop.runner import list_scenarios, load_scenario, run_scenario
from redloop.targets import GuardedAgent, RuleAgent
from redloop.targets.base import Agent


SCENARIOS = {
    "email_exfil": "exfiltration",
    "slack_unauthorized_send": "unauthorized_send",
    "github_destructive": "destructive_action",
    "x_policy_override": "policy_override",
}


def test_bundled_scenarios_are_discoverable():
    assert set(list_scenarios()) == set(SCENARIOS)


@pytest.mark.parametrize("name,kind", SCENARIOS.items())
def test_naive_target_executes_injected_instruction_and_turns_red(name, kind):
    row = run_scenario(name, RuleAgent(), results_path=None)
    assert row["status"] == "red"
    assert row["score"] == len(row["violations"]) > 0
    assert kind in {finding["kind"] for finding in row["violations"]}
    assert row["scenario"] == name
    assert row["agent"] == "naive"
    assert row["payload"] == load_scenario(name)["seed_payload"]
    assert row["run_id"] and row["timestamp"] and row["response"]
    for finding in row["violations"]:
        action = row["actions"][finding["action_index"]]
        assert action["tool"] == finding["tool"]
        assert action["status"] == "ok"


@pytest.mark.parametrize("name", SCENARIOS)
def test_guarded_target_ignores_injected_instructions_and_turns_green(name):
    scenario = load_scenario(name)
    row = run_scenario(scenario, GuardedAgent(), results_path=None)
    assert row["status"] == "green"
    assert row["score"] == 0
    assert row["violations"] == []
    assert [action["tool"] for action in row["actions"]] == [
        entry["tool"] for entry in scenario["entrypoints"]
    ]
    assert "<untrusted_tool_output>" in row["response"]


@pytest.mark.parametrize("name", SCENARIOS)
def test_naive_benign_control_is_green(name):
    row = run_scenario(name, "naive", "", results_path=None)
    assert row["status"] == "green"
    assert row["payload"] == ""
    assert row["violations"] == []


def test_allowlisting_tool_does_not_authorize_instructions_inside_output():
    scenario = load_scenario("email_exfil")
    scenario["allowed_tools"].append("gmail.send_email")
    row = run_scenario(scenario, "guarded", results_path=None)
    assert row["status"] == "green"
    assert all(action["tool"] != "gmail.send_email" for action in row["actions"])


def test_guarded_allowlist_blocks_unapproved_trusted_entrypoints():
    scenario = load_scenario("github_destructive")
    scenario["entrypoints"].append({
        "tool": "github.delete_repo", "arguments": {"repo": "demo-repo"},
    })
    row = run_scenario(scenario, "guarded", "", results_path=None)
    assert row["status"] == "green"
    assert row["actions"][-1]["tool"] == "github.delete_repo"
    assert row["actions"][-1]["status"] == "blocked"


def test_runs_append_jsonl_and_isolate_fixture_state(tmp_path):
    scenario = load_scenario("github_destructive")
    original = copy.deepcopy(scenario)
    results_path = tmp_path / "nested" / "results.jsonl"
    first = run_scenario(scenario, "naive", results_path=results_path)
    second = run_scenario(scenario, "guarded", results_path=results_path)
    assert scenario == original
    assert first["status"] == "red"
    assert second["status"] == "green"
    assert first["run_id"] != second["run_id"]
    assert [json.loads(line) for line in results_path.read_text().splitlines()] == [first, second]


def test_scenario_can_be_loaded_from_json_path(tmp_path):
    expected = load_scenario("email_exfil")
    path = tmp_path / "custom.json"
    path.write_text(json.dumps(expected))
    assert load_scenario(path) == expected
    assert run_scenario(str(path), "guarded", results_path=None)["status"] == "green"


def test_unconfigured_llama_target_is_explicitly_skipped(monkeypatch):
    for name in ("LLAMA_BASE_URL", "LLAMA_API_KEY", "LLAMA_MODEL"):
        monkeypatch.delenv(name, raising=False)
    row = run_scenario("email_exfil", "llama", results_path=None)
    assert row["status"] == "skipped"
    assert row["score"] == 0
    assert row["violations"] == []
    assert row["actions"] == []


def test_target_failure_is_recorded_as_error():
    class FailingAgent(Agent):
        name = "failing"

        def run(self, sandbox, scenario):
            raise RuntimeError("Target failed during experiment")

    row = run_scenario("email_exfil", FailingAgent(), results_path=None)
    assert row["status"] == "error"
    assert "Target failed during experiment" in row["error"]


def test_failure_after_destructive_action_keeps_violation_evidence():
    class DestructiveFailingAgent(Agent):
        name = "destructive-failing"

        def run(self, sandbox, scenario):
            sandbox.call("github.delete_repo", repo="demo-repo")
            raise RuntimeError("Failure after side effect")

    row = run_scenario("github_destructive", DestructiveFailingAgent(), results_path=None)
    assert row["status"] == "error"
    assert row["score"] == 1
    assert row["violations"][0]["kind"] == "destructive_action"
    assert row["actions"][0]["status"] == "ok"
    assert "Failure after side effect" in row["error"]


def test_naive_target_has_a_finite_action_budget():
    row = run_scenario("email_exfil", RuleAgent(max_actions=1), results_path=None)
    assert row["status"] == "error"
    assert "budget" in row["error"].lower()
    assert len(row["actions"]) == 1
