"""In-memory document store tools."""

from typing import Any

from .base import Sandbox, require_string, tool


def _doc(sandbox: Sandbox, doc_id: str) -> dict[str, Any]:
    require_string(doc_id, "doc_id")
    docs = sandbox.state.get("docs", {}).get("files", {})
    if doc_id not in docs or docs[doc_id].get("deleted", False):
        raise ValueError(f"Unknown document: {doc_id}")
    return docs[doc_id]


@tool("docs.read_doc")
def read_doc(sandbox: Sandbox, doc_id: str) -> dict[str, Any]:
    return _doc(sandbox, doc_id)


@tool("docs.share_doc")
def share_doc(sandbox: Sandbox, doc_id: str, email: str) -> dict[str, Any]:
    require_string(email, "email")
    shared = _doc(sandbox, doc_id).setdefault("shared_with", [])
    shared.append(email)
    return {"doc_id": doc_id, "shared_with": list(shared)}


@tool("docs.delete_doc")
def delete_doc(sandbox: Sandbox, doc_id: str) -> dict[str, Any]:
    _doc(sandbox, doc_id)["deleted"] = True
    return {"doc_id": doc_id, "deleted": True}
