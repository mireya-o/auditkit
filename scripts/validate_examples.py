from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]

required = [
    root / "README.md",
    root / "docs" / "ARCHITECTURE.md",
    root / "docs" / "VALIDATION.md",
    root / "docs" / "DESIGN_DECISIONS.md",
    root / "docs" / "FAILURE_MODES.md",
    root / "SECURITY.md",
    root / "examples" / "audit_pack_sample.json",
]

missing = [str(p.relative_to(root)) for p in required if not p.exists()]
if missing:
    raise SystemExit(f"Missing required files: {missing}")

p = root / "examples" / "audit_pack_sample.json"
json.loads(p.read_text(encoding="utf-8"))

print("example validation: OK")
