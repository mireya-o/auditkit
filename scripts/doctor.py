from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv(*args, **kwargs):  # type: ignore
        return False


def ok(msg: str) -> None:
    print(f"OK   {msg}")


def warn(msg: str) -> None:
    print(f"WARN {msg}")


def fail(msg: str) -> None:
    print(f"FAIL {msg}")


def env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v and v.strip() else default


def list_models(base_url: str) -> list[str]:
    url = base_url.rstrip("/") + "/models"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = []
    for item in data.get("data", []):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            out.append(item["id"])
    return out


def main() -> int:
    load_dotenv()

    base_url = env("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
    chat_model = env("LMSTUDIO_CHAT_MODEL", "openai/gpt-oss-20b")
    embed_model = env("LMSTUDIO_EMBED_MODEL", "text-embedding-nomic-embed-text-v1.5-embedding")
    raw_dir = Path(env("AUDITKIT_RAW_DIR", "data/raw"))
    index_dir = Path(env("AUDITKIT_INDEX_DIR", "data/index"))

    required_raw = [
        "eu_ai_act_timeline_implementation.pdf",
        "nist_ai_600-1_genai_profile.pdf",
        "nist_ir_8596_cyber_ai_profile_iprd.pdf",
        "owasp_top10_llm_apps_v2025.pdf",
    ]

    print("AuditKit doctor")
    print(f"base_url:   {base_url}")
    print(f"raw_dir:    {raw_dir}")
    print(f"index_dir:  {index_dir}")
    print(f"chat:       {chat_model}")
    print(f"vector:     {embed_model}")
    print("")

    hard_failures: list[str] = []

    if raw_dir.exists():
        missing = [name for name in required_raw if not (raw_dir / name).exists()]
        if missing:
            hard_failures.append(f"missing source files: {missing}")
        else:
            ok(f"bounded source set present ({len(required_raw)} files)")
    else:
        hard_failures.append(f"missing directory: {raw_dir}")

    models: list[str] = []
    try:
        models = list_models(base_url)
        ok(f"runtime reachable ({len(models)} profiles detected)")
    except urllib.error.URLError as e:
        hard_failures.append(f"runtime not reachable at {base_url}: {e.reason}")
    except Exception as e:
        hard_failures.append(f"runtime check failed at {base_url}: {e}")

    if models:
        if chat_model in models:
            ok("configured response profile present")
        else:
            hard_failures.append(f"configured response profile not found: {chat_model}")

        if embed_model in models:
            ok("configured vector profile present")
        else:
            hard_failures.append(f"configured vector profile not found: {embed_model}")

    index_files = [
        index_dir / "index.faiss",
        index_dir / "chunks.jsonl",
        index_dir / "meta.json",
    ]
    missing_index = [p.name for p in index_files if not p.exists()]
    if missing_index:
        warn(f"local index not present ({missing_index})")
        warn("next step: make index")
    else:
        ok("local index present")

    print("")
    if hard_failures:
        for item in hard_failures:
            fail(item)
        print("")
        print("RESULT: FAIL")
        return 1

    if missing_index:
        print("RESULT: OK_WITH_WARNINGS")
    else:
        print("RESULT: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
