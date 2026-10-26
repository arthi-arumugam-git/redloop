from pathlib import Path

from redloop.cli import main

ROOT = Path(__file__).resolve().parents[1]
SUITE = str(ROOT / "results/regression_suite.json")


def test_guarded_green_unguarded_demo_red():
    assert main(["check-suite", "--suite", SUITE, "--agent", "guarded"]) == 0
    assert main(["check-suite", "--suite", SUITE, "--agent", "naive"]) == 1


def test_demo_workflow_is_manual_only_and_keeps_guard():
    wf = (ROOT / ".github/workflows/demo-red-vs-green.yml").read_text()
    assert "on: workflow_dispatch" in wf
    assert "--agent guarded" in wf and "--agent naive" in wf
