import json

from app.missions.evolution import MissionAdmissionProposal, MissionEvolutionEngine, MissionFit, ValueAssessment
from app.missions.evolution_runtime import EvolutionRuntimeError, MissionEvolutionRuntime


def _proposal():
    fit = MissionFit("A", "INSUFFICIENT", "PARTIAL", "INSUFFICIENT", "INSUFFICIENT", "SUFFICIENT", "SUFFICIENT", "PARTIAL", "INSUFFICIENT", True, False, ("e:a",), "gap")
    value = ValueAssessment(*(["SUBSTANTIAL"] * 9), *(["LOW"] * 5), "POSITIVE", "material gap", ("e:value",))
    centrality = {"downstream_dependencies": 1, "tasks_enabled": 2, "scientific_importance": "HIGH", "risk_reduction": "HIGH", "validation_importance": "HIGH", "cross_mission_relevance": "HIGH", "frequency_of_required_use": "RECURRING", "irreversibility_if_missing": "HIGH", "decision_impact": "HIGH"}
    return MissionAdmissionProposal("PROP-RUNTIME", "X", "Persistent capability is required.", ("capability",), (fit,), "No existing mission is sufficient.", "Collaboration is persistently discontinuous.", "NEW-RUNTIME", ("capability",), ("unrelated work",), value, "LOW", ("mission registry",), "least privilege", "preserve provenance", "provider-neutral", ("zero-context",), ("retire when value disappears",), centrality=centrality)


def _decision():
    proposal = _proposal()
    fit = proposal.current_missions_audited
    return MissionEvolutionEngine([{"mission_id": "A", "canonical_name": "A", "mission_type": "TEST", "status": "ACTIVE"}]).decide(
        action_x="X", necessity=True, fits=fit, collaboration_sufficient=False, temporary_task_force_sufficient=False,
        coherence=True, integrability=True, validatability=True, marginal_value=proposal.expected_marginal_value,
        centrality=proposal.centrality, proposal=proposal)


def test_admission_is_persisted_and_discoverable(tmp_path):
    root = tmp_path
    missions = root / "docs" / "missions"
    missions.mkdir(parents=True)
    (missions / "MISSION_REGISTRY.json").write_text(json.dumps({"missions": [{"mission_id": "A", "canonical_name": "A", "mission_type": "TEST", "status": "ACTIVE"}]}), encoding="utf-8")
    runtime = MissionEvolutionRuntime(root)
    decision = _decision()
    staged = runtime.stage_admission(decision, {"CAN_AUTHORIZE": True})
    assert staged.exists()
    runtime.commit_staged("PROP-RUNTIME", {"CAN_AUTHORIZE": True})
    result = runtime.validate_zero_context("NEW-RUNTIME")
    assert result["passed"] is True
    assert result["next"].startswith("LOAD_CONTRACT")


def test_stale_admission_fails_closed(tmp_path):
    root = tmp_path
    missions = root / "docs" / "missions"
    missions.mkdir(parents=True)
    (missions / "MISSION_REGISTRY.json").write_text(json.dumps({"missions": [{"mission_id": "A", "canonical_name": "A", "mission_type": "TEST", "status": "ACTIVE"}]}), encoding="utf-8")
    runtime = MissionEvolutionRuntime(root)
    runtime.stage_admission(_decision(), {"CAN_AUTHORIZE": True})
    (missions / "MISSION_REGISTRY.VERSION").write_text("different-version", encoding="utf-8")
    try:
        runtime.commit_staged("PROP-RUNTIME", {"CAN_AUTHORIZE": True})
    except EvolutionRuntimeError as exc:
        assert "STALE_REGISTRY_VERSION" in str(exc)
    else:
        raise AssertionError("stale admission must fail closed")
