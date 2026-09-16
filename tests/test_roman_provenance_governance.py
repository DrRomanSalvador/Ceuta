import json
from pathlib import Path

from app.missions.registry import MissionRegistry

ROOT = Path(__file__).resolve().parents[1]
ROMAN = ROOT / "docs/missions/roman"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_generated_output_cannot_be_admitted_as_authentic_source_by_corpus_contract():
    corpus = _json(ROMAN / "ROMAN_SOURCE_CORPUS.json")
    assert corpus["mission_id"] == "ROMAN"
    assert corpus["source_policy"].startswith("Only explicitly authorized")
    assert corpus["generated_output_policy"].startswith("Outputs produced by ROMAN")
    assert corpus["sources"] == []
    assert set(corpus["required_source_fields"]) >= {
        "source_id", "source_type", "locator", "date", "authorization",
        "content_hash", "provenance", "evidence_status",
    }


def test_source_corpus_does_not_self_authorize_or_promote_generated_content():
    corpus = _json(ROMAN / "ROMAN_SOURCE_CORPUS.json")
    assert corpus["admission_status"] == "READY_FOR_AUTHORIZED_CORPUS"
    assert corpus["next_action"].startswith("Populate only with authorized source material")
    for source in corpus["sources"]:
        assert source.get("authorization") not in (None, "generated", "model_output")
        assert source.get("evidence_status") not in ("generated", "synthetic", "model_output")


def test_roman_identity_and_control_plane_identity_are_semantically_separate():
    registry = MissionRegistry(ROOT)
    mission = registry.get("ROMAN")
    control = _json(ROOT / "docs/missions/UNIVERSAL_EXECUTION_STATE.json")
    assert mission["mission_id"] == "ROMAN"
    assert mission["mission_type"] == "AUTHORIAL_INTELLECTUAL_FORENSIC"
    assert control["control_id"] == "UNIVERSAL_EXECUTION_CONTROL"
    assert control["control_id"] != mission["mission_id"]


def test_later_unverified_head_is_never_promoted_as_verified_evidence():
    state = _json(ROMAN / "ROMAN_MISSION_STATE.json")
    reconciliation = state["current_state_reconciliation"]
    verified = state["last_verified_state"]
    if reconciliation["current_head"] != verified["HEAD"]:
        assert reconciliation["current_head_checks"] in {"NO_CHECK_RUNS_YET", "PENDING_EXACT_HEAD_CI_SECURITY"}
    else:
        assert reconciliation["current_head_checks"] in {
            "CI_SUCCESS_AND_SECURITY_SUCCESS",
            "PR_HEAD_ASSOCIATED_CI_SECURITY_SUCCESS_EXACT_BRANCH_HEAD_UNVERIFIED",
        }
    security_state = state["security_state"]
    assert (
        verified["HEAD"] in security_state
        or verified["HEAD"][:12] in security_state
        or verified["HEAD"][:8] in security_state
    )


def test_continuation_pointer_preserves_exact_head_validation_boundary():
    state = _json(ROMAN / "ROMAN_MISSION_STATE.json")
    pointer = state["continuation_pointer"]
    assert pointer["mission_id"] == "ROMAN"
    assert pointer["mission_type"] == "AUTHORIAL_INTELLECTUAL_FORENSIC"
    assert pointer["last_verified_head"] == state["last_verified_state"]["HEAD"]
    assert pointer["validation_requirement"].startswith("Only exact-head evidence")
    assert pointer["stopping_condition"].startswith("Only exhaustion-gate proof")
