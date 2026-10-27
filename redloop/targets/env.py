"""Resolve model endpoint env vars. LLAMA_* wins; MUSE_*/META_* map in with Meta defaults."""
from __future__ import annotations

import os

META_DEFAULT_BASE_URL = "https://api.meta.ai/v1"
META_DEFAULT_MODEL = "muse-spark-1.3"
NEBIUS_DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1"
NEBIUS_DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"


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
    nebius_key = _get("NEBIUS_API_KEY")
    if nebius_key and not key:  # Nebius Token Factory + NVIDIA Nemotron preset
        return {
            "LLAMA_BASE_URL": _get("NEBIUS_BASE_URL") or NEBIUS_DEFAULT_BASE_URL,
            "LLAMA_API_KEY": nebius_key,
            "LLAMA_MODEL": _get("NEBIUS_MODEL") or NEBIUS_DEFAULT_MODEL,
        }
    if key and not _get("LLAMA_API_KEY"):  # key came from MUSE_/META_/MODEL_API_KEY
        base = base or META_DEFAULT_BASE_URL
        model = model or META_DEFAULT_MODEL
    return {"LLAMA_BASE_URL": base, "LLAMA_API_KEY": key, "LLAMA_MODEL": model}
