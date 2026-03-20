from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Tuple

import streamlit as st


# --- Make src/ importable without requiring PYTHONPATH ---
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from auditkit.rag import RAG  # noqa: E402
from auditkit.settings import load_settings  # noqa: E402
from auditkit.lmstudio_client import LMStudioClient  # noqa: E402
from auditkit.audit_pack import export_audit_pack, generate_audit_pack  # noqa: E402


def split_answer_and_sources(md: str) -> Tuple[str, str]:
    if not md:
        return "", ""
    m = re.search(r"\n### Sources\s*\n", md)
    if not m:
        return md.strip(), ""
    i = m.start()
    answer = md[:i].strip()
    sources = md[i:].strip()
    return answer, sources


@st.cache_data
def load_index_meta() -> dict[str, Any]:
    meta_path = ROOT / "data" / "index" / "meta.json"
    if not meta_path.exists():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


@st.cache_resource
def get_rag() -> RAG:
    return RAG()


@st.cache_data
def list_lmstudio_models(base_url: str, timeout_s: float) -> list[str]:
    try:
        c = LMStudioClient(base_url=base_url, timeout_s=timeout_s)
        try:
            return c.models()
        finally:
            c.close()
    except Exception:
        return []


def load_example_description() -> str:
    p = ROOT / "docs" / "operator_input_template.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


st.set_page_config(page_title="AuditKit", page_icon="🧭", layout="wide")

s = load_settings()

st.title("AuditKit")
st.caption("Grounded answers, control mapping, and audit-ready exports over bounded source sets.")

with st.sidebar:
    st.subheader("Runtime")

    st.write("**LM Studio base URL**")
    st.code(s.base_url, language="text")

    st.write("**Models (expected)**")
    st.write(f"- Chat: `{s.chat_model}`")
    st.write(f"- Embeddings: `{s.embed_model}`")

    models = list_lmstudio_models(s.base_url, s.request_timeout_s)
    if models:
        st.write("**Models (detected via /v1/models)**")
        st.code("\n".join(models), language="text")
    else:
        st.warning("Could not list models. Is LM Studio server running on 127.0.0.1:1234?")

    st.divider()
    st.subheader("Index")

    meta = load_index_meta()
    if meta:
        st.write(f"- PDFs: **{meta.get('pdfs')}**")
        st.write(f"- Pages: **{meta.get('pages')}**")
        st.write(f"- Chunks: **{meta.get('chunks')}**")
        st.write(f"- Embedding dim: **{meta.get('embedding_dim')}**")
        files = meta.get("files") or []
        if files:
            with st.expander("Indexed files"):
                for f in files:
                    st.write(f"- {f.get('file')} ({f.get('bytes')} bytes)")
    else:
        st.error("Index metadata not found. Did you run `python -m auditkit.build_index`?")

    st.divider()
    if st.button("Reload caches (if you rebuilt the index)", type="secondary"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Caches cleared. Streamlit will reload resources on next interaction.")


tab_ask, tab_pack = st.tabs(["Ask", "Audit Pack"])

with tab_ask:
    st.subheader("Ask (grounded answers with citations)")

    q = st.text_area(
        "Question",
        placeholder="Example: What is prompt injection and why is it risky?",
        height=90,
        key="ask_question",
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        top_k = st.slider("top_k", min_value=2, max_value=12, value=int(s.top_k), step=1, key="ask_topk")
    with col2:
        max_tokens = st.slider("max_tokens", min_value=200, max_value=1200, value=650, step=50, key="ask_maxtok")
    with col3:
        st.write("")
        st.write("")
        run = st.button("Ask", type="primary", use_container_width=True, key="ask_btn")

    if run:
        if not q.strip():
            st.warning("Please enter a question.")
        else:
            try:
                rag = get_rag()
                res = rag.answer(q.strip(), top_k=int(top_k), max_tokens=int(max_tokens))
                st.success(f"Done in {res['latency_s']}s")

                answer_md, sources_md = split_answer_and_sources(res["answer_markdown"])

                st.markdown("### Answer")
                st.markdown(answer_md)

                if sources_md.strip():
                    with st.expander("Sources", expanded=True):
                        st.markdown(sources_md)

                with st.expander("Retrieved context (debug)", expanded=False):
                    for c in res["contexts"]:
                        flag = "⚠️" if c.get("flagged_injection") else ""
                        st.markdown(
                            f"**[{c['key']}]** {flag} `{c['source']}` p{c['page']} — score={c['score']:.4f}"
                        )
                        st.code(c["text"], language="text")

                st.caption("Cited keys: " + (", ".join(res.get("cited_keys", [])) or "(none)"))

            except Exception as e:
                st.error("Error while answering. Check that LM Studio server is running and the index exists.")
                st.exception(e)

with tab_pack:
    st.subheader("Audit Pack (MD + JSON export)")

    default_desc = load_example_description()
    system_desc = st.text_area(
        "System description (free text or structured)",
        value=default_desc,
        height=260,
        key="pack_desc",
    )

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        per_query_top_k = st.slider("per_query_top_k", 3, 10, 6, 1, key="pack_pqk")
    with c2:
        max_contexts = st.slider("max_contexts", 6, 16, 8, 1, key="pack_mctx")
    with c3:
        pack_tokens = st.slider("max_tokens", 700, 1600, 1200, 50, key="pack_tok")
    with c4:
        st.write("")
        st.write("")
        gen = st.button("Generate Audit Pack", type="primary", use_container_width=True, key="pack_btn")

    if gen:
        if not system_desc.strip():
            st.warning("Please provide a system description.")
        else:
            try:
                rag = get_rag()
                with st.spinner("Generating audit pack..."):
                    res = generate_audit_pack(
                        rag,
                        system_desc.strip(),
                        per_query_top_k=int(per_query_top_k),
                        max_contexts=int(max_contexts),
                        max_tokens=int(pack_tokens),
                    )

                paths = export_audit_pack(res, out_dir=ROOT / "exports")
                st.success(
                    "Generated successfully.\n\n"
                    f"- markdown: {paths['markdown']}\n"
                    f"- json: {paths['json']}\n"
                    f"- latency: {res.latency_s}s"
                )

                st.markdown(res.markdown)

                with st.expander("JSON (validated)", expanded=False):
                    st.code(json.dumps(res.pack_dict, ensure_ascii=False, indent=2), language="json")

                st.download_button(
                    "Download Markdown",
                    data=res.markdown.encode("utf-8"),
                    file_name="audit_pack.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
                st.download_button(
                    "Download JSON",
                    data=json.dumps(res.pack_dict, ensure_ascii=False, indent=2).encode("utf-8"),
                    file_name="audit_pack.json",
                    mime="application/json",
                    use_container_width=True,
                )

                with st.expander("Contexts used (debug)", expanded=False):
                    st.write("Used snippet keys: " + (", ".join(res.used_keys) if res.used_keys else "(none)"))
                    for c in res.contexts:
                        flag = "⚠️" if c.flagged_injection else ""
                        st.markdown(f"**[{c.key}]** {flag} `{c.source}` p{c.page} — score={c.score:.4f}")
                        st.code(c.text, language="text")

            except Exception as e:
                st.error("Error while generating the audit pack.")
                st.exception(e)
