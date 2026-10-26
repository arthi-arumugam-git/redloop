
import pytest as _pytest


@_pytest.fixture(autouse=True)
def _single_http_attempt(monkeypatch):
    """Fake endpoints script one response per call; retries are covered in test_http_retry."""
    monkeypatch.setenv("REDLOOP_HTTP_ATTEMPTS", "1")
