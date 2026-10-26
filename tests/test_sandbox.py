"""Behavioral coverage for local mock tools and fixture injection."""

import copy
import json
from pathlib import Path

import pytest

from redloop.sandbox import Sandbox, TOOL_SCHEMAS, inject
from redloop.sandbox import gmail, github, slack, x


SCENARIOS = Path(__file__).resolve().parents[1] / "redloop" / "scenarios"


def scenario(name):
    return json.loads((SCENARIOS / f"{name}.json").read_text())


def complete_state():
    state = {}
    for name in ("email_exfil", "slack_unauthorized_send", "github_destructive", "x_policy_override"):
        state.update(scenario(name)["state"])
    return state


def test_every_tool_dispatches_and_records_its_action():
    sandbox = Sandbox(complete_state())
    calls = [
        ("gmail.list_inbox", {}),
        ("gmail.read_email", {"email_id": "email-1"}),
        ("gmail.send_email", {"to": "analyst@example.test", "subject": "Report", "body": "Done"}),
        ("slack.list_messages", {"channel": "#team"}),
        ("slack.post_message", {"channel": "#team", "text": "Done"}),
        ("github.list_issues", {"repo": "demo-repo"}),
        ("github.read_issue", {"repo": "demo-repo", "issue_id": "1"}),
        ("github.comment_issue", {"repo": "demo-repo", "issue_id": "1", "body": "Reviewed"}),
        ("github.delete_repo", {"repo": "demo-repo"}),
        ("x.read_timeline", {}),
        ("x.post", {"text": "Reviewed"}),
    ]
    for tool, arguments in calls:
        result = sandbox.call(tool, **arguments)
        assert sandbox.action_log[-1] == {
            "tool": tool, "arguments": arguments, "status": "ok", "result": result
        }
    assert len(sandbox.action_log) == len(calls)
    assert sandbox.state["gmail"]["sent"][-1]["body"] == "Done"
    assert sandbox.state["slack"]["channels"]["#team"][-1]["text"] == "Done"
    repo = sandbox.state["github"]["repos"]["demo-repo"]
    assert repo["issues"][0]["comments"][-1]["body"] == "Reviewed"
    assert repo["deleted"] is True
    assert sandbox.state["x"]["posts"][-1]["text"] == "Reviewed"
    json.dumps(sandbox.action_log, allow_nan=False)


@pytest.mark.parametrize("function,arguments", [
    (gmail.list_inbox, {}),
    (gmail.read_email, {"email_id": "email-1"}),
    (gmail.send_email, {"to": "analyst@example.test", "subject": "Report", "body": "Done"}),
    (slack.list_messages, {"channel": "#team"}),
    (slack.post_message, {"channel": "#team", "text": "Done"}),
    (github.list_issues, {"repo": "demo-repo"}),
    (github.read_issue, {"repo": "demo-repo", "issue_id": "1"}),
    (github.comment_issue, {"repo": "demo-repo", "issue_id": "1", "body": "Reviewed"}),
    (github.delete_repo, {"repo": "demo-repo"}),
    (x.read_timeline, {}),
    (x.post, {"text": "Reviewed"}),
])
def test_direct_tool_functions_record_actions(function, arguments):
    sandbox = Sandbox(complete_state())
    result = function(sandbox, **arguments)
    assert len(sandbox.action_log) == 1
    assert sandbox.action_log[0]["result"] == result
    assert sandbox.action_log[0]["arguments"] == arguments


def test_state_returns_and_logs_are_independent_snapshots():
    initial = complete_state()
    sandbox = Sandbox(initial)
    initial["gmail"]["inbox"][0]["body"] = "Changed outside sandbox"
    email = sandbox.call("gmail.read_email", email_id="email-1")
    original = email["body"]
    email["body"] = "Changed returned result"
    assert sandbox.state["gmail"]["inbox"][0]["body"] == original
    assert sandbox.action_log[0]["result"]["body"] == original
    sandbox.state["gmail"]["inbox"][0]["body"] = "Changed internal state"
    assert sandbox.action_log[0]["result"]["body"] == original
    posted = sandbox.call("x.post", text="Hello")
    posted["text"] = "Changed post result"
    assert sandbox.state["x"]["posts"][-1]["text"] == "Hello"


@pytest.mark.parametrize("tool,arguments", [
    ("missing.tool", {}),
    ("gmail.read_email", {"email_id": "missing"}),
    ("gmail.read_email", {}),
    ("gmail.list_inbox", {"unexpected": "argument"}),
    ("slack.list_messages", {"channel": "#missing"}),
    ("github.read_issue", {"repo": "missing", "issue_id": "1"}),
    ("github.read_issue", {"repo": "demo-repo", "issue_id": "missing"}),
    ("gmail.send_email", {"to": "", "subject": "Report", "body": "Done"}),
    ("x.post", {"text": 42}),
])
def test_failed_actions_are_logged_without_mutating_state(tool, arguments):
    sandbox = Sandbox(complete_state())
    before = copy.deepcopy(sandbox.state)
    with pytest.raises(ValueError):
        sandbox.call(tool, **arguments)
    assert sandbox.state == before
    assert len(sandbox.action_log) == 1
    assert sandbox.action_log[0]["tool"] == tool
    assert sandbox.action_log[0]["status"] == "error"
    assert sandbox.action_log[0]["error"]


def test_direct_tool_failure_is_logged_and_deleted_repo_is_inaccessible():
    sandbox = Sandbox(complete_state())
    with pytest.raises(ValueError):
        gmail.read_email(sandbox, "missing")
    assert sandbox.action_log[-1]["status"] == "error"
    github.delete_repo(sandbox, "demo-repo")
    with pytest.raises(ValueError, match="deleted"):
        github.list_issues(sandbox, "demo-repo")
    assert len(sandbox.action_log) == 3


def test_non_json_arguments_produce_a_serializable_error_record():
    sandbox = Sandbox(complete_state())
    with pytest.raises(ValueError, match="JSON serializable"):
        sandbox.call("x.post", text=object())
    assert sandbox.action_log[-1]["status"] == "error"
    json.dumps(sandbox.action_log, allow_nan=False)


def test_blocked_action_preserves_argument_snapshot():
    sandbox = Sandbox({})
    arguments = {"to": ["attacker@example.test"]}
    sandbox.record_blocked("gmail.send_email", arguments, "Tool not allowed")
    arguments["to"].append("another@example.test")
    assert sandbox.action_log == [{
        "tool": "gmail.send_email", "arguments": {"to": ["attacker@example.test"]},
        "status": "blocked", "reason": "Tool not allowed",
    }]


@pytest.mark.parametrize("state", [[], {"invalid": object()}, {"invalid": float("nan")}])
def test_sandbox_rejects_non_json_object_state(state):
    with pytest.raises(ValueError):
        Sandbox(state)


@pytest.mark.parametrize("name", ["email_exfil", "slack_unauthorized_send", "github_destructive", "x_policy_override"])
def test_fixture_injection_reaches_legitimate_tool_output(name):
    item = scenario(name)
    state = copy.deepcopy(item["state"])
    assert inject(state, item["seed_payload"], item["injection_location"]) is state
    sandbox = Sandbox(state)
    outputs = [sandbox.call(entry["tool"], **entry["arguments"]) for entry in item["entrypoints"]]
    assert item["seed_payload"] in json.dumps(outputs).replace('\\"', '"')
    assert {entry["tool"] for entry in item["entrypoints"]} <= set(item["allowed_tools"])


def test_inject_appends_and_preserves_other_values():
    state = {"inbox": [{"body": "Legitimate text", "subject": "Hello"}]}
    inject(state, "malicious text", "inbox.0.body")
    assert state == {"inbox": [{"body": "Legitimate text\nmalicious text", "subject": "Hello"}]}


@pytest.mark.parametrize("location", ["", "inbox.9.body", "inbox.-1.body", "inbox.bad.body", "missing.body", "inbox.0.missing", "inbox.0", "inbox.0.body.extra", ".inbox.0.body"])
def test_invalid_injection_is_atomic(location):
    state = {"inbox": [{"body": "Original"}]}
    before = copy.deepcopy(state)
    with pytest.raises(ValueError):
        inject(state, "Payload", location)
    assert state == before


def test_tool_schemas_cover_the_dispatch_api():
    names = {schema["function"]["name"] for schema in TOOL_SCHEMAS}
    assert names == {
        "gmail.list_inbox", "gmail.read_email", "gmail.send_email",
        "slack.list_messages", "slack.post_message", "github.list_issues",
        "github.read_issue", "github.comment_issue", "github.delete_repo",
        "x.read_timeline", "x.post",
        "calendar.list_events", "calendar.create_event", "calendar.delete_event",
        "docs.read_doc", "docs.share_doc", "docs.delete_doc",
        "crm.get_contact", "crm.update_contact", "crm.delete_contact",
        "tickets.list_tickets", "tickets.read_ticket", "tickets.read_attachment",
    }
    from redloop.sandbox.base import _TOOLS
    assert names == set(_TOOLS)
    assert all(schema["type"] == "function" for schema in TOOL_SCHEMAS)
    assert all(schema["function"]["parameters"]["type"] == "object" for schema in TOOL_SCHEMAS)
