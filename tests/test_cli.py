"""Exercise the installed module boundary without writing project results."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from redloop.runner import load_scenario


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {"email_exfil", "slack_unauthorized_send", "github_destructive", "x_policy_override"}


def cli(*arguments):
    env = os.environ.copy()
    for name in ("LLAMA_BASE_URL", "LLAMA_API_KEY", "LLAMA_MODEL"):
        env.pop(name, None)
    return subprocess.run(
        [sys.executable, "-m", "redloop", *arguments], cwd=ROOT,
        capture_output=True, text=True, env=env, timeout=20,
    )


def test_list_shows_all_scenarios():
    process = cli("list")
    assert process.returncode == 0, process.stderr
    assert all(name in process.stdout for name in SCENARIOS)


@pytest.mark.parametrize("agent,status,label", [
    ("naive", "red", "RED"),
    ("guarded", "green", "GREEN"),
    ("llama", "skipped", "SKIP"),
])
def test_all_scenario_cli_reports_expected_results(tmp_path, agent, status, label):
    path = tmp_path / "results.jsonl"
    process = cli("run", "--all", "--agent", agent, "--results", str(path))
    assert process.returncode == 0, process.stderr
    assert label in process.stdout
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert {row["scenario"] for row in rows} == SCENARIOS
    assert len(rows) == 4
    assert all(row["status"] == status for row in rows)


def test_default_run_selects_email_and_naive(tmp_path):
    path = tmp_path / "results.jsonl"
    process = cli("run", "--results", str(path))
    assert process.returncode == 0, process.stderr
    row = json.loads(path.read_text())
    assert (row["scenario"], row["agent"], row["status"]) == ("email_exfil", "naive", "red")


def test_all_overrides_single_scenario_and_empty_payload_is_benign(tmp_path):
    path = tmp_path / "results.jsonl"
    process = cli(
        "run", "--scenario", "email_exfil", "--all", "--agent", "naive",
        "--payload", "", "--results", str(path),
    )
    assert process.returncode == 0, process.stderr
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows) == 4
    assert all(row["status"] == "green" for row in rows)


@pytest.mark.parametrize("arguments", [
    ("run", "--agent", "unknown"),
    ("run", "--scenario", "unknown"),
])
def test_invalid_selection_returns_usage_error(tmp_path, arguments):
    path = tmp_path / "results.jsonl"
    process = cli(*arguments, "--results", str(path))
    assert process.returncode == 2
    assert "error" in process.stderr.lower()
    assert not path.exists()


def test_target_execution_error_returns_exit_one_and_preserves_result(tmp_path):
    scenario = load_scenario("email_exfil")
    scenario["entrypoints"] = [{"tool": "unknown.tool", "arguments": {}}]
    scenario_path = tmp_path / "invalid-entrypoint.json"
    scenario_path.write_text(json.dumps(scenario))
    results_path = tmp_path / "results.jsonl"
    process = cli("run", "--scenario", str(scenario_path), "--results", str(results_path))
    assert process.returncode == 1
    assert "ERROR" in process.stdout
    row = json.loads(results_path.read_text())
    assert row["status"] == "error"
    assert row["actions"][0]["status"] == "error"
