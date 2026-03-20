import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_audit_pack_sample_has_expected_top_level_shape() -> None:
    sample = json.loads((ROOT / "examples" / "audit_pack_sample.json").read_text(encoding="utf-8"))

    required = {
        "disclaimer",
        "system_card",
        "risk_register",
        "owasp_llm_top10_mapping",
        "nist_function_mapping",
        "eu_ai_act_timeline",
        "operational_checklist",
    }
    assert required.issubset(sample.keys())

    assert len(sample["risk_register"]) == 10
    assert len(sample["owasp_llm_top10_mapping"]) == 10
    assert len(sample["eu_ai_act_timeline"]) >= 3

    functions = {item["function"] for item in sample["nist_function_mapping"]}
    assert functions == {"GOVERN", "MAP", "MEASURE", "MANAGE"}

    checklist = sample["operational_checklist"]
    assert {"pre_release", "post_release", "monitoring", "incident_response"}.issubset(checklist.keys())


def test_example_markdown_artifacts_exist() -> None:
    assert (ROOT / "examples" / "audit_pack_sample.md").exists()
    assert (ROOT / "examples" / "evaluation_sample.md").exists()
    assert (ROOT / "examples" / "adversarial_sample.md").exists()
