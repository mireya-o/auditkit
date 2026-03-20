from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any

from rich.console import Console
from rich.table import Table

from .rag import RAG


def _now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _is_insufficient(answer_md: str) -> bool:
    return (answer_md or "").strip().lower().startswith("i don't have enough information")


def _split_answer_only(answer_md: str) -> str:
    # Remove the generated sources section for format checks.
    md = (answer_md or "").strip()
    marker = "\n### Sources\n"
    i = md.find(marker)
    return md if i == -1 else md[:i].strip()


def _is_strict_bullets(answer_only: str) -> bool:
    if _is_insufficient(answer_only):
        return True
    lines = [ln.strip() for ln in (answer_only or "").splitlines() if ln.strip()]
    if not lines:
        return False
    return all(ln.startswith("- ") for ln in lines)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _load_index_meta() -> dict[str, Any]:
    meta_path = Path("data/index/meta.json")
    if not meta_path.exists():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


@dataclass
class Metrics:
    n_total: int
    n_errors: int
    n_insufficient: int
    citation_rate: float
    pass_rate: float
    avg_latency_s: float
    retrieved_expected_avg: float | None
    cited_expected_avg: float | None


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate AuditKit RAG on a small JSONL dataset.")
    parser.add_argument("--input", type=str, default="data/eval/questions.jsonl")
    parser.add_argument("--out_dir", type=str, default="exports")
    parser.add_argument("--top_k", type=int, default=6)
    parser.add_argument("--max_tokens", type=int, default=650)
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)

    if not in_path.exists():
        raise SystemExit(f"Input dataset not found: {in_path}")

    examples = _load_jsonl(in_path)
    if not examples:
        raise SystemExit("No examples found in dataset.")

    console = Console()
    console.print("[bold]AuditKit[/bold] eval")
    console.print(f"dataset: {in_path} | examples: {len(examples)} | top_k={args.top_k} | max_tokens={args.max_tokens}")

    meta = _load_index_meta()
    if meta:
        console.print(f"index: pdfs={meta.get('pdfs')} pages={meta.get('pages')} chunks={meta.get('chunks')} dim={meta.get('embedding_dim')}")

    rag = RAG()
    results: list[dict[str, Any]] = []

    t_all0 = time.time()

    try:
        for ex in examples:
            qid = str(ex.get("id", ""))
            question = str(ex.get("question", "")).strip()
            expected_sources = ex.get("expected_sources") or []
            expect_insufficient = bool(ex.get("expect_insufficient", False))

            if not question:
                continue

            rec: dict[str, Any] = {
                "id": qid,
                "question": question,
                "expected_sources": expected_sources,
                "expect_insufficient": expect_insufficient,
            }

            t0 = time.time()
            try:
                res = rag.answer(question, top_k=int(args.top_k), max_tokens=int(args.max_tokens))
                latency_s = float(res.get("latency_s", round(time.time() - t0, 3)))
                answer_md = str(res.get("answer_markdown", ""))
                cited_keys = list(res.get("cited_keys", []))
                contexts = list(res.get("contexts", []))

                answer_only = _split_answer_only(answer_md)
                insufficient = _is_insufficient(answer_only)
                format_ok = _is_strict_bullets(answer_only)

                key_to_source = {c["key"]: c["source"] for c in contexts if "key" in c and "source" in c}
                retrieved_sources = sorted({c.get("source") for c in contexts if isinstance(c, dict) and c.get("source")})
                cited_sources = sorted({key_to_source[k] for k in cited_keys if k in key_to_source})

                exp = set(expected_sources)
                ret = set(retrieved_sources)
                cit = set(cited_sources)

                retrieved_expected_cov = (len(exp & ret) / len(exp)) if exp else None
                cited_expected_cov = (len(exp & cit) / len(exp)) if exp else None

                # pass logic:
                if expect_insufficient:
                    passed = insufficient
                else:
                    passed = (not insufficient) and (len(cited_keys) > 0) and (cited_expected_cov is None or cited_expected_cov > 0.0)

                rec.update(
                    {
                        "latency_s": latency_s,
                        "insufficient": insufficient,
                        "format_ok": format_ok,
                        "cited_keys": cited_keys,
                        "retrieved_sources": retrieved_sources,
                        "cited_sources": cited_sources,
                        "retrieved_expected_coverage": retrieved_expected_cov,
                        "cited_expected_coverage": cited_expected_cov,
                        "passed": passed,
                        "answer_preview": answer_only[:380],
                    }
                )

            except Exception as e:
                latency_s = round(time.time() - t0, 3)
                rec.update(
                    {
                        "latency_s": latency_s,
                        "error": f"{type(e).__name__}: {e}",
                        "passed": False,
                    }
                )

            results.append(rec)

    finally:
        rag.close()

    total_s = time.time() - t_all0

    n_total = len(results)
    n_errors = sum(1 for r in results if "error" in r)
    n_insufficient = sum(1 for r in results if r.get("insufficient") is True)

    # citation rate computed on non-insufficient & non-error
    valid = [r for r in results if "error" not in r and not r.get("insufficient")]
    citation_rate = (sum(1 for r in valid if (r.get("cited_keys") or [])) / len(valid)) if valid else 0.0

    pass_rate = sum(1 for r in results if r.get("passed") is True) / max(n_total, 1)
    avg_latency = sum(float(r.get("latency_s", 0.0)) for r in results) / max(n_total, 1)

    # coverage averages (ignore None + errors)
    ret_covs = [r.get("retrieved_expected_coverage") for r in results if isinstance(r.get("retrieved_expected_coverage"), (int, float))]
    cit_covs = [r.get("cited_expected_coverage") for r in results if isinstance(r.get("cited_expected_coverage"), (int, float))]

    retrieved_expected_avg = (sum(ret_covs) / len(ret_covs)) if ret_covs else None
    cited_expected_avg = (sum(cit_covs) / len(cit_covs)) if cit_covs else None

    m = Metrics(
        n_total=n_total,
        n_errors=n_errors,
        n_insufficient=n_insufficient,
        citation_rate=round(citation_rate, 3),
        pass_rate=round(pass_rate, 3),
        avg_latency_s=round(avg_latency, 3),
        retrieved_expected_avg=(round(retrieved_expected_avg, 3) if retrieved_expected_avg is not None else None),
        cited_expected_avg=(round(cited_expected_avg, 3) if cited_expected_avg is not None else None),
    )

    ts = _now_ts()
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / f"eval_results_{ts}.jsonl"
    report_path = out_dir / f"eval_report_{ts}.md"
    _write_jsonl(results_path, results)

    # Build markdown report
    lines: list[str] = []
    lines.append(f"# AuditKit Evaluation Report ({ts} UTC)")
    lines.append("")
    lines.append("## Summary metrics")
    lines.append(f"- Total examples: **{m.n_total}**")
    lines.append(f"- Errors: **{m.n_errors}**")
    lines.append(f"- Insufficient answers: **{m.n_insufficient}**")
    lines.append(f"- Pass rate: **{m.pass_rate}**")
    lines.append(f"- Citation rate (non-insufficient, non-error): **{m.citation_rate}**")
    lines.append(f"- Avg latency (s): **{m.avg_latency_s}**")
    lines.append(f"- Total runtime (s): **{round(total_s, 1)}**")
    lines.append("")
    lines.append("## Source coverage")
    lines.append(f"- Retrieved expected coverage (avg): **{m.retrieved_expected_avg if m.retrieved_expected_avg is not None else 'N/A'}**")
    lines.append(f"- Cited expected coverage (avg): **{m.cited_expected_avg if m.cited_expected_avg is not None else 'N/A'}**")
    lines.append("")
    if meta:
        lines.append("## Index metadata")
        lines.append(f"- PDFs: {meta.get('pdfs')} | Pages: {meta.get('pages')} | Chunks: {meta.get('chunks')} | Dim: {meta.get('embedding_dim')}")
        lines.append("")

    lines.append("## Per-example results")
    lines.append("| id | passed | insufficient | latency_s | cited_sources | expected_sources |")
    lines.append("|---:|:------:|:------------:|----------:|---------------|------------------|")
    for r in results:
        cid = r.get("id", "")
        passed = "✅" if r.get("passed") else "❌"
        ins = "yes" if r.get("insufficient") else "no"
        lat = r.get("latency_s", "")
        cited = ", ".join(r.get("cited_sources", [])[:2]) if isinstance(r.get("cited_sources"), list) else ""
        exp = ", ".join(r.get("expected_sources", [])[:2]) if isinstance(r.get("expected_sources"), list) else ""
        lines.append(f"| {cid} | {passed} | {ins} | {lat} | {cited} | {exp} |")

    # Failure details
    failures = [r for r in results if not r.get("passed")]
    if failures:
        lines.append("")
        lines.append("## Failures (details)")
        for r in failures:
            lines.append(f"### {r.get('id','')}")
            lines.append(f"- Question: {r.get('question','')}")
            if r.get("error"):
                lines.append(f"- Error: `{r.get('error')}`")
            lines.append(f"- Expected sources: {r.get('expected_sources', [])}")
            lines.append(f"- Retrieved sources: {r.get('retrieved_sources', [])}")
            lines.append(f"- Cited sources: {r.get('cited_sources', [])}")
            lines.append(f"- Answer preview: {r.get('answer_preview','')}")
            lines.append("")

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    # Console table (quick glance)
    t = Table(title="AuditKit eval summary")
    t.add_column("Metric")
    t.add_column("Value")
    t.add_row("examples", str(m.n_total))
    t.add_row("errors", str(m.n_errors))
    t.add_row("insufficient", str(m.n_insufficient))
    t.add_row("pass_rate", str(m.pass_rate))
    t.add_row("citation_rate", str(m.citation_rate))
    t.add_row("avg_latency_s", str(m.avg_latency_s))
    if m.retrieved_expected_avg is not None:
        t.add_row("retrieved_expected_avg", str(m.retrieved_expected_avg))
    if m.cited_expected_avg is not None:
        t.add_row("cited_expected_avg", str(m.cited_expected_avg))
    console.print(t)

    console.print("[green]OK[/green] wrote:")
    console.print(f"- {results_path}")
    console.print(f"- {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
