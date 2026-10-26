import io
import urllib.error
import urllib.request

import pytest

from redloop.http_retry import backoff_delay, is_transient, urlopen_with_retries


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def _http_error(code):
    return urllib.error.HTTPError("http://x", code, "err", {}, io.BytesIO(b""))


def _opener(outcomes):
    calls = []

    def opener(request, timeout):
        calls.append(timeout)
        item = outcomes.pop(0)
        if isinstance(item, BaseException):
            raise item
        return _Resp(item)

    return opener, calls


REQ = urllib.request.Request("http://example.invalid", data=b"{}", method="POST")


def test_retries_transient_then_succeeds():
    opener, calls = _opener([_http_error(503), urllib.error.URLError("reset"), b'{"ok":1}'])
    slept = []
    assert urlopen_with_retries(REQ, 5, attempts=3, sleep=slept.append, opener=opener) == b'{"ok":1}'
    assert len(calls) == 3 and len(slept) == 2


def test_non_transient_fails_fast():
    opener, calls = _opener([_http_error(401), b"never"])
    with pytest.raises(urllib.error.HTTPError):
        urlopen_with_retries(REQ, 5, attempts=3, sleep=lambda s: None, opener=opener)
    assert len(calls) == 1


def test_gives_up_after_attempts():
    opener, calls = _opener([_http_error(429)] * 3)
    with pytest.raises(urllib.error.HTTPError):
        urlopen_with_retries(REQ, 5, attempts=3, sleep=lambda s: None, opener=opener)
    assert len(calls) == 3


def test_transient_classification_and_backoff():
    assert is_transient(_http_error(429)) and is_transient(TimeoutError())
    assert not is_transient(_http_error(400)) and not is_transient(ValueError())
    assert backoff_delay(0, retry_after="2") == 2.0
    assert 0 < backoff_delay(10) <= 8.0
