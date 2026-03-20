from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
import warnings

from pypdf import PdfReader
from pypdf.errors import PdfReadWarning


@dataclass(frozen=True)
class DocumentPage:
    source: str
    page: int
    text: str


def normalize_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\x00", "")
    lines = [ln.strip() for ln in text.splitlines()]
    joined = " ".join([ln for ln in lines if ln])
    joined = " ".join(joined.split())
    return joined.strip()


def iter_pdf_pages(pdf_path: Path) -> Iterator[DocumentPage]:
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    source = pdf_path.name

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=PdfReadWarning)
        try:
            reader = PdfReader(str(pdf_path), strict=False)
        except TypeError:
            reader = PdfReader(str(pdf_path))

    if getattr(reader, "is_encrypted", False):
        try:
            reader.decrypt("")
        except Exception as e:
            raise RuntimeError(f"PDF is encrypted and cannot be read: {pdf_path}") from e

    for i, page in enumerate(reader.pages):
        raw = page.extract_text() or ""
        txt = normalize_text(raw)
        if len(txt) < 40:
            continue
        yield DocumentPage(source=source, page=i + 1, text=txt)
