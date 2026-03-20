from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v.strip() != "" else default


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v)
    except ValueError as e:
        raise ValueError(f"Environment variable {name} must be an int, got {v!r}") from e


def _env_float(name: str, default: float) -> float:
    v = os.environ.get(name)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except ValueError as e:
        raise ValueError(f"Environment variable {name} must be a float, got {v!r}") from e


@dataclass(frozen=True)
class Settings:
    base_url: str
    chat_model: str
    embed_model: str
    raw_dir: Path
    index_dir: Path
    chunk_size_chars: int
    chunk_overlap_chars: int
    embed_batch_size: int
    request_timeout_s: float
    top_k: int


def load_settings() -> Settings:
    base_url = _env("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
    chat_model = _env("LMSTUDIO_CHAT_MODEL", "openai/gpt-oss-20b")
    embed_model = _env("LMSTUDIO_EMBED_MODEL", "text-embedding-nomic-embed-text-v1.5-embedding")

    raw_dir = Path(_env("AUDITKIT_RAW_DIR", "data/raw"))
    index_dir = Path(_env("AUDITKIT_INDEX_DIR", "data/index"))

    chunk_size_chars = _env_int("AUDITKIT_CHUNK_SIZE_CHARS", 1400)
    chunk_overlap_chars = _env_int("AUDITKIT_CHUNK_OVERLAP_CHARS", 220)
    embed_batch_size = _env_int("AUDITKIT_EMBED_BATCH_SIZE", 32)

    request_timeout_s = _env_float("AUDITKIT_REQUEST_TIMEOUT_S", 120.0)
    top_k = _env_int("AUDITKIT_TOP_K", 6)

    if chunk_overlap_chars >= chunk_size_chars:
        raise ValueError("AUDITKIT_CHUNK_OVERLAP_CHARS must be < AUDITKIT_CHUNK_SIZE_CHARS")

    return Settings(
        base_url=base_url,
        chat_model=chat_model,
        embed_model=embed_model,
        raw_dir=raw_dir,
        index_dir=index_dir,
        chunk_size_chars=chunk_size_chars,
        chunk_overlap_chars=chunk_overlap_chars,
        embed_batch_size=embed_batch_size,
        request_timeout_s=request_timeout_s,
        top_k=top_k,
    )
