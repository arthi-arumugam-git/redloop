"""Resolve model endpoint env vars. LLAMA_* wins; MUSE_*/META_* map in with Meta defaults."""
from __future__ import annotations

import os

META_DEFAULT_BASE_URL = "https://api.meta.ai/v1"
META_DEFAULT_MODEL = "muse-spark-1.3"


def _get(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def resolve_llama_env() -> dict[str, str]:
    key = _get("LLAMA_API_KEY", "MUSE_API_KEY", "META_API_KEY", "MODEL_API_KEY")
    base = _get("LLAMA_BASE_URL", "MUSE_BASE_URL", "META_BASE_URL")
    model = _get("LLAMA_MODEL", "MUSE_MODEL", "META_MODEL")
    if key and not _get("LLAMA_API_KEY"):  # key came from MUSE_/META_/MODEL_API_KEY
        base = base or META_DEFAULT_BASE_URL
        model = model or META_DEFAULT_MODEL
    return {"LLAMA_BASE_URL": base, "LLAMA_API_KEY": key, "LLAMA_MODEL": model}
