from redloop.sandbox.base import Sandbox


def test_list_docs_hides_deleted_and_needs_no_id_guessing():
    sandbox = Sandbox({"docs": {"files": {
        "doc-a": {"title": "A", "body": "x"},
        "doc-b": {"title": "B", "body": "y", "deleted": True},
    }}})
    assert sandbox.call("docs.list_docs") == [{"doc_id": "doc-a", "title": "A"}]
