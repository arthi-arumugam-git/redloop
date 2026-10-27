
import pytest as _pytest


@_pytest.fixture(autouse=True)
def _single_http_attempt(monkeypatch):
    """Fake endpoints script one response per call; retries are covered in test_http_retry."""
    monkeypatch.setenv("REDLOOP_HTTP_ATTEMPTS", "1")


@_pytest.fixture(autouse=True)
def _no_ambient_meta_keys(monkeypatch):
    """Box env may hold a real META_API_KEY; offline tests must never see it."""
    for name in ("META_API_KEY", "MUSE_API_KEY", "MODEL_API_KEY", "MUSE_BASE_URL",
                 "META_BASE_URL", "MUSE_MODEL", "META_MODEL",
                 "NEBIUS_API_KEY", "NEBIUS_BASE_URL", "NEBIUS_MODEL"):
        monkeypatch.delenv(name, raising=False)
