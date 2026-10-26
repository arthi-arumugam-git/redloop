"""Retry transient model-endpoint failures with capped exponential backoff.

Production runs hit rate limits (429) and flaky gateways (5xx, resets). A red-team
suite that dies on one 503 is not CI-safe, so model calls retry before giving up.
Non-transient errors (400/401/403/404) fail immediately.
"""

from __future__ import annotations

import os
import random
import time
import urllib.error
import urllib.request
from typing import Callable

TRANSIENT_HTTP = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


def _attempts() -> int:
    try:
        return max(1, int(os.environ.get("REDLOOP_HTTP_ATTEMPTS", "3")))
    except ValueError:
        return 3


def is_transient(exc: BaseException) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in TRANSIENT_HTTP
    return isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError))


def backoff_delay(attempt: int, base: float = 0.5, cap: float = 8.0, retry_after: str | None = None) -> float:
    if retry_after:
        try:
            return min(cap, max(0.0, float(retry_after)))
        except ValueError:
            pass
    return min(cap, base * (2 ** attempt)) * (0.5 + random.random() / 2)


def urlopen_with_retries(
    request: urllib.request.Request,
    timeout: float,
    attempts: int | None = None,
    sleep: Callable[[float], None] = time.sleep,
    opener: Callable[..., object] | None = None,
) -> bytes:
    """Open ``request`` and return the body (up to 1 MiB + 1 byte), retrying transient failures."""
    opener = opener or urllib.request.urlopen  # late-bound so tests/monkeypatching work
    total = attempts if attempts is not None else _attempts()
    for attempt in range(total):
        try:
            with opener(request, timeout=timeout) as response:  # type: ignore[attr-defined]
                return response.read(1_048_577)
        except Exception as exc:  # noqa: BLE001 - re-raised unchanged when not retryable
            if attempt + 1 >= total or not is_transient(exc):
                raise
            retry_after = None
            if isinstance(exc, urllib.error.HTTPError):
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                exc.close()
            sleep(backoff_delay(attempt, retry_after=retry_after))
    raise AssertionError("unreachable")
