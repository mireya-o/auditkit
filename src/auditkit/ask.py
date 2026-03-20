from __future__ import annotations

import argparse
from rich.console import Console
from rich.markdown import Markdown

from .rag import RAG


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask AuditKit (local RAG) and print answer + sources.")
    parser.add_argument("question", nargs="+")
    parser.add_argument("--top_k", type=int, default=None)
    args = parser.parse_args()

    question = " ".join(args.question).strip()

    console = Console()
    rag = RAG()
    try:
        res = rag.answer(question, top_k=args.top_k)
    finally:
        rag.close()

    console.print(f"[bold]Latency:[/bold] {res['latency_s']}s\n")
    md = res["answer_markdown"] or "(empty answer)"
    console.print(Markdown(md))

    console.print("\n[bold]Cited keys:[/bold] " + (", ".join(res.get("cited_keys", [])) or "(none)"))

    # Debug list for UI integration later
    ctx = res["contexts"]
    console.print("\n[bold]Retrieved snippets:[/bold]")
    for c in ctx:
        console.print(f"- {c['key']}  {c['source']} p{c['page']}  score={c['score']:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
