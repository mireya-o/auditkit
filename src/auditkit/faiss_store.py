from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import faiss
import numpy as np

from .chunking import Chunk


@dataclass(frozen=True)
class IndexPaths:
    index_faiss: Path
    chunks_jsonl: Path
    meta_json: Path


def default_paths(index_dir: Path) -> IndexPaths:
    return IndexPaths(
        index_faiss=index_dir / "index.faiss",
        chunks_jsonl=index_dir / "chunks.jsonl",
        meta_json=index_dir / "meta.json",
    )


def build_index(embeddings: np.ndarray) -> faiss.Index:
    if embeddings.ndim != 2:
        raise ValueError("embeddings must be a 2D array")
    d = int(embeddings.shape[1])
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    return index


def save_index(index: faiss.Index, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(path))


def load_index(path: Path) -> faiss.Index:
    return faiss.read_index(str(path))


def write_chunks_jsonl(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            rec = {
                "id": c.id,
                "source": c.source,
                "page": c.page,
                "chunk_index": c.chunk_index,
                "char_start": c.char_start,
                "char_end": c.char_end,
                "text": c.text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_chunks_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def write_meta(meta: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
