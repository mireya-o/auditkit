from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from .audit_pack import export_audit_pack, generate_audit_pack
from .rag import RAG


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an Audit Pack (MD + JSON) from a system description.")
    parser.add_argument("--input", type=str, default="", help="Path to a text/markdown file containing the system description.")
    parser.add_argument("--text", type=str, default="", help="System description as a string.")
    parser.add_argument("--per_query_top_k", type=int, default=6)
    parser.add_argument("--max_contexts", type=int, default=14)
    parser.add_argument("--max_tokens", type=int, default=1800)
    parser.add_argument("--out_dir", type=str, default="exports")
    args = parser.parse_args()

    if args.input:
        p = Path(args.input)
        if not p.exists():
            raise SystemExit(f"--input file not found: {p}")
        system_description = p.read_text(encoding="utf-8")
    else:
        system_description = args.text

    system_description = (system_description or "").strip()
    if not system_description:
        raise SystemExit("Provide --input or --text with a non-empty system description.")

    console = Console()
    console.print("[bold]AuditKit[/bold] generate_pack")

    rag = RAG()
    try:
        res = generate_audit_pack(
            rag,
            system_description,
            per_query_top_k=int(args.per_query_top_k),
            max_contexts=int(args.max_contexts),
            max_tokens=int(args.max_tokens),
        )
    finally:
        rag.close()

    paths = export_audit_pack(res, out_dir=args.out_dir)

    console.print(f"[green]OK[/green] generated in {res.latency_s}s")
    console.print(f"- markdown: {paths['markdown']}")
    console.print(f"- json:     {paths['json']}")
    console.print(f"- used snippet keys: {', '.join(res.used_keys) if res.used_keys else '(none)'}")
    console.print(f"- risks: {len(res.pack.risk_register)} | owasp_map: {len(res.pack.owasp_llm_top10_mapping)} | nist_map: {len(res.pack.nist_function_mapping)} | eu_timeline: {len(res.pack.eu_ai_act_timeline)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
