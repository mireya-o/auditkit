from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    page: int
    chunk_index: int
    char_start: int
    char_end: int
    text: str


def make_chunk_id(source: str, page: int, chunk_index: int) -> str:
    return f"{source}::p{page}::c{chunk_index}"


def chunk_text(
    source: str,
    page: int,
    text: str,
    chunk_size_chars: int,
    overlap_chars: int,
) -> list[Chunk]:
    if overlap_chars >= chunk_size_chars:
        raise ValueError("overlap_chars must be < chunk_size_chars")

    t = " ".join(text.split())
    n = len(t)
    if n == 0:
        return []

    chunks: list[Chunk] = []
    start = 0
    idx = 0

    while start < n:
        end = min(n, start + chunk_size_chars)

        if end < n:
            window = t[start:end]
            cut = -1
            for sep in (". ", "? ", "! ", "; ", ": ", "\n"):
                pos = window.rfind(sep)
                if pos > cut:
                    cut = pos
            if cut != -1 and cut >= int(chunk_size_chars * 0.6):
                end = start + cut + 1

        if end <= start:
            end = min(n, start + chunk_size_chars)

        chunk_txt = t[start:end].strip()
        if chunk_txt:
            chunks.append(
                Chunk(
                    id=make_chunk_id(source, page, idx),
                    source=source,
                    page=page,
                    chunk_index=idx,
                    char_start=start,
                    char_end=end,
                    text=chunk_txt,
                )
            )
            idx += 1

        if end >= n:
            break
        start = max(0, end - overlap_chars)

    return chunks
