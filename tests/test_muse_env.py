import urllib.error

import pytest

from redloop.judge import llm_judge
from redloop.targets.env import META_DEFAULT_BASE_URL, META_DEFAULT_MODEL, resolve_llama_env

NAMES = ("LLAMA_BASE_URL", "LLAMA_API_KEY", "LLAMA_MODEL")


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    for n in NAMES + ("JUDGE_BASE_URL", "JUDGE_API_KEY", "JUDGE_MODEL"):
        monkeypatch.delenv(n, raising=False)


def test_meta_key_alone_gets_muse_defaults(monkeypatch):
    monkeypatch.setenv("META_API_KEY", "fake")
    assert resolve_llama_env() == {
        "LLAMA_BASE_URL": META_DEFAULT_BASE_URL, "LLAMA_API_KEY": "fake", "LLAMA_MODEL": META_DEFAULT_MODEL}
    assert META_DEFAULT_MODEL == "muse-spark-1.3"


def test_muse_vars_override_defaults(monkeypatch):
    monkeypatch.setenv("MUSE_API_KEY", "k")
    monkeypatch.setenv("MUSE_MODEL", "muse-spark-1.2")
    assert resolve_llama_env()["LLAMA_MODEL"] == "muse-spark-1.2"


def test_llama_vars_win_and_no_meta_defaults(monkeypatch):
    monkeypatch.setenv("LLAMA_API_KEY", "l")
    monkeypatch.setenv("META_API_KEY", "m")
    env = resolve_llama_env()
    assert env == {"LLAMA_BASE_URL": "", "LLAMA_API_KEY": "l", "LLAMA_MODEL": ""}


def test_nothing_set_is_empty():
    assert resolve_llama_env() == dict.fromkeys(NAMES, "")


def test_judge_falls_back_to_meta(monkeypatch):
    monkeypatch.setenv("META_API_KEY", "fake")
    assert llm_judge._config()["MODEL"] == META_DEFAULT_MODEL


def test_judge_http_error_is_error_not_safe(monkeypatch):
    def boom(*a, **k):
        raise urllib.error.HTTPError("u", 403, "restricted", {}, None)
    monkeypatch.setattr(llm_judge, "urlopen_with_retries", boom)
    j = llm_judge.ChatLLMJudge.__new__(llm_judge.ChatLLMJudge)
    j.timeout = 1
    with pytest.raises(llm_judge.JudgeError, match="403"):
        j._http("http://x/v1/chat/completions", "k", {})
