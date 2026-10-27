from redloop.targets.env import NEBIUS_DEFAULT_BASE_URL, NEBIUS_DEFAULT_MODEL, resolve_llama_env

ALL = ("LLAMA_BASE_URL", "LLAMA_API_KEY", "LLAMA_MODEL", "NEBIUS_API_KEY", "NEBIUS_BASE_URL", "NEBIUS_MODEL")


def _clear(mp):
    for n in ALL:
        mp.delenv(n, raising=False)


def test_nebius_defaults(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("NEBIUS_API_KEY", "nk")
    assert resolve_llama_env() == {"LLAMA_BASE_URL": NEBIUS_DEFAULT_BASE_URL, "LLAMA_API_KEY": "nk",
                                   "LLAMA_MODEL": NEBIUS_DEFAULT_MODEL}


def test_nebius_overrides(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("NEBIUS_API_KEY", "nk")
    monkeypatch.setenv("NEBIUS_MODEL", "nvidia/nemotron-3-super-120b-a12b")
    assert resolve_llama_env()["LLAMA_MODEL"] == "nvidia/nemotron-3-super-120b-a12b"


def test_llama_key_wins_over_nebius(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("NEBIUS_API_KEY", "nk")
    monkeypatch.setenv("LLAMA_API_KEY", "lk")
    assert resolve_llama_env()["LLAMA_API_KEY"] == "lk"
