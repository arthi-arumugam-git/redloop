"""Each defense layer alone must keep the frozen regression suite green."""

from pathlib import Path

import pytest

from redloop.cli import main
from redloop.targets import make_agent

SUITE = Path(__file__).resolve().parents[1] / "results" / "regression_suite.json"


@pytest.mark.parametrize("agent", ["guarded", "spotlight-only", "allowlist-only"])
def test_each_layer_blocks_suite(agent, capsys):
    assert main(["check-suite", "--suite", str(SUITE), "--agent", agent]) == 0
    assert f"{agent}: 0/" in capsys.readouterr().out


def test_naive_still_red(capsys):
    assert main(["check-suite", "--suite", str(SUITE), "--agent", "naive"]) == 1


def test_ablation_flags():
    s, a = make_agent("spotlight-only"), make_agent("allowlist-only")
    assert (s.spotlight, s.allowlist, s.name) == (True, False, "spotlight-only")
    assert (a.spotlight, a.allowlist, a.name) == (False, True, "allowlist-only")
