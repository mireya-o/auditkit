from __future__ import annotations

import argparse
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import faiss
import numpy as np
from rich.console import Console
from rich.progress import track

from .chunking import Chunk, chunk_text
from .faiss_store import build_index, default_paths, save_index, write_chunks_jsonl, write_meta
from .lmstudio_client import LMStudioClient
from .pdf_ingest import iter_pdf_pages
from .settings import load_settings


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    s = load_settings()

    parser = argparse.ArgumentParser(
        description="Build a local FAISS (cosine/IP) index from PDFs using LM Studio embeddings."
    )
    parser.add_argument("--raw_dir", default=str(s.raw_dir))
    parser.add_argument("--index_dir", default=str(s.index_dir))
    parser.add_argument("--embed_model", default=s.embed_model)
    parser.add_argument("--chunk_size", type=int, default=s.chunk_size_chars)
    parser.add_argument("--overlap", type=int, default=s.chunk_overlap_chars)
    parser.add_argument("--batch_size", type=int, default=s.embed_batch_size)
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    index_dir = Path(args.index_dir)
    embed_model = str(args.embed_model)
    chunk_size = int(args.chunk_size)
    overlap = int(args.overlap)
    batch_size = int(args.batch_size)

    console = Console()
    console.print("[bold]AuditKit[/bold] build_index")
    console.print(f"base_url: {s.base_url}")
    console.print(f"raw_dir: {raw_dir}")
    console.print(f"index_dir: {index_dir}")
    console.print(f"embed_model: {embed_model}")
    console.print(f"chunk_size_chars: {chunk_size} | overlap_chars: {overlap} | batch_size: {batch_size}")

    pdf_paths = sorted(raw_dir.glob("*.pdf"))
    if not pdf_paths:
        raise SystemExit(f"No PDFs found in {raw_dir}")

    client = LMStudioClient(base_url=s.base_url, timeout_s=s.request_timeout_s)
    try:
        available = client.models()
        if embed_model not in available:
            raise SystemExit(f"Embedding model {embed_model!r} not available. /v1/models returned: {available}")

        pages_total = 0
        chunks: list[Chunk] = []
        file_fingerprints: list[dict[str, str | int]] = []

        for pdf in pdf_paths:
            file_fingerprints.append(
                {
                    "file": pdf.name,
                    "bytes": int(pdf.stat().st_size),
                    "sha256": sha256_file(pdf),
                }
            )
            for page in iter_pdf_pages(pdf):
                pages_total += 1
                chunks.extend(
                    chunk_text(
                        source=page.source,
                        page=page.page,
                        text=page.text,
                        chunk_size_chars=chunk_size,
                        overlap_chars=overlap,
                    )
                )

        if not chunks:
            raise SystemExit("No chunks produced. PDFs may be empty/unextractable.")

        console.print(f"pdfs: {len(pdf_paths)} | pages: {pages_total} | chunks: {len(chunks)}")

        texts = [c.text for c in chunks]
        vectors: list[list[float]] = []

        t0 = time.time()
        for i in track(range(0, len(texts), batch_size), description="Embedding chunks"):
            batch = texts[i : i + batch_size]
            vecs = client.embeddings(model=embed_model, inputs=batch)
            vectors.extend(vecs)
        dt = time.time() - t0

        if len(vectors) != len(chunks):
            raise SystemExit(f"Embedding count mismatch: got {len(vectors)} vectors for {len(chunks)} chunks")

        emb = np.asarray(vectors, dtype="float32")
        if emb.ndim != 2:
            raise SystemExit(f"Embeddings array is not 2D: shape={emb.shape}")

        faiss.normalize_L2(emb)
        index = build_index(emb)

        paths = default_paths(index_dir)
        save_index(index, paths.index_faiss)
        write_chunks_jsonl(chunks, paths.chunks_jsonl)

        meta = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "base_url": s.base_url,
            "embed_model": embed_model,
            "embedding_dim": int(emb.shape[1]),
            "chunks": int(len(chunks)),
            "pages": int(pages_total),
            "pdfs": int(len(pdf_paths)),
            "files": file_fingerprints,
            "chunking": {
                "chunk_size_chars": int(chunk_size),
                "overlap_chars": int(overlap),
            },
        }
        write_meta(meta, paths.meta_json)

        console.print("[green]OK[/green] wrote:")
        console.print(f"- {paths.index_faiss}")
        console.print(f"- {paths.chunks_jsonl}")
        console.print(f"- {paths.meta_json}")
        console.print(f"embedding_time_s: {dt:.1f} | chunks_per_s: {len(chunks)/max(dt,1e-9):.2f}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
