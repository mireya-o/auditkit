from __future__ import annotations

import argparse
from pathlib import Path

import faiss
import numpy as np
from rich.console import Console

from .faiss_store import default_paths, load_index, read_chunks_jsonl
from .lmstudio_client import LMStudioClient
from .settings import load_settings


def main() -> int:
    s = load_settings()

    parser = argparse.ArgumentParser(description="Search the local FAISS index (LM Studio embeddings).")
    parser.add_argument("query", nargs="+")
    parser.add_argument("--top_k", type=int, default=s.top_k)
    parser.add_argument("--embed_model", default=s.embed_model)
    parser.add_argument("--index_dir", default=str(s.index_dir))
    args = parser.parse_args()

    query = " ".join(args.query).strip()
    top_k = int(args.top_k)
    embed_model = str(args.embed_model)
    index_dir = Path(args.index_dir)

    console = Console()
    paths = default_paths(index_dir)

    index = load_index(paths.index_faiss)
    chunks = read_chunks_jsonl(paths.chunks_jsonl)

    client = LMStudioClient(base_url=s.base_url, timeout_s=s.request_timeout_s)
    try:
        vec = client.embeddings(model=embed_model, inputs=[query])[0]
    finally:
        client.close()

    q = np.asarray([vec], dtype="float32")
    faiss.normalize_L2(q)

    scores, ids = index.search(q, top_k)
    scores = scores[0].tolist()
    ids = ids[0].tolist()

    console.print(f"[bold]Query:[/bold] {query}")
    console.print(f"[bold]Top {top_k} results[/bold]")

    for rank, (idx, score) in enumerate(zip(ids, scores), start=1):
        if idx == -1:
            continue
        rec = chunks[idx]
        snippet = rec["text"][:240].replace("\n", " ")
        console.print(f"\n#{rank}  score={score:.4f}  {rec['id']}")
        console.print(f"source={rec['source']}  page={rec['page']}")
        console.print(snippet)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
