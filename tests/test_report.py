import json

from redloop.cli import main
from redloop.dashboard_data import markdown_report


def _rows():
    return [
        {"scenario": "email_exfil", "agent": "naive", "status": "red"},
        {"scenario": "email_exfil", "agent": "naive", "status": "green"},
        {"scenario": "email_exfil", "agent": "guarded", "status": "green"},
        {"scenario": "x_policy_override", "agent": "naive", "status": "red"},
        {"scenario": "x_policy_override", "agent": "guarded", "status": "skipped"},
    ]


def test_markdown_report_pivot_and_overall():
    table = markdown_report(_rows())
    assert "| Scenario | guarded ASR | naive ASR |" in table
    assert "| email_exfil | 0% (0/1) | 50% (1/2) |" in table
    assert "| x_policy_override | n/a | 100% (1/1) |" in table
    assert "**0% (0/1)**" in table and "**67% (2/3)**" in table


def test_markdown_report_empty():
    assert markdown_report([]) == "_No results yet._\n"


def test_report_cli_writes_file(tmp_path, capsys):
    results = tmp_path / "r.jsonl"
    results.write_text("\n".join(json.dumps(r) for r in _rows()) + "\nnot json\n")
    out = tmp_path / "asr.md"
    assert main(["report", "--results", str(results), "--out", str(out)]) == 0
    assert "naive ASR" in capsys.readouterr().out
    assert out.read_text().startswith("| Scenario |")
