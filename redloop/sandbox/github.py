"""In-memory GitHub tools. Deletion is a simulated state flag."""

from typing import Any

from .base import Sandbox, require_string, tool


def _repo(sandbox: Sandbox, repo: str) -> dict[str, Any]:
    require_string(repo, "repo")
    repos = sandbox.state.get("github", {}).get("repos", {})
    if repo not in repos:
        raise ValueError(f"Unknown repository: {repo}")
    if repos[repo].get("deleted", False):
        raise ValueError(f"Repository has been deleted: {repo}")
    return repos[repo]


def _issue(sandbox: Sandbox, repo: str, issue_id: str) -> dict[str, Any]:
    require_string(issue_id, "issue_id")
    for issue in _repo(sandbox, repo).get("issues", []):
        if issue.get("id") == issue_id:
            return issue
    raise ValueError(f"Unknown issue: {repo}#{issue_id}")


@tool("github.list_issues")
def list_issues(sandbox: Sandbox, repo: str) -> list[dict[str, Any]]:
    return [
        {key: issue[key] for key in ("id", "title") if key in issue}
        for issue in _repo(sandbox, repo).get("issues", [])
    ]


@tool("github.read_issue")
def read_issue(sandbox: Sandbox, repo: str, issue_id: str) -> dict[str, Any]:
    return _issue(sandbox, repo, issue_id)


@tool("github.comment_issue")
def comment_issue(sandbox: Sandbox, repo: str, issue_id: str, body: str) -> dict[str, Any]:
    require_string(body, "body")
    issue = _issue(sandbox, repo, issue_id)
    comments = issue.setdefault("comments", [])
    comment = {"id": f"comment-{len(comments) + 1}", "body": body}
    comments.append(comment)
    return comment


@tool("github.delete_repo")
def delete_repo(sandbox: Sandbox, repo: str) -> dict[str, Any]:
    _repo(sandbox, repo)["deleted"] = True
    return {"repo": repo, "deleted": True}
