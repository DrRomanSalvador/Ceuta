import json

from app.missions.evolution import MissionAdmissionProposal, MissionEvolutionEngine, MissionFit, ValueAssessment
from app.missions.evolution_runtime import EvolutionRuntimeError, MissionEvolutionRuntime


def _proposal():
    fit = MissionFit("A", "INSUFFICIENT", "PARTIAL", "INSUFFICIENT", "INSUFFICIENT", "SUFFICIENT", "SUFFICIENT", "PARTIAL", "INSUFFICIENT", True, False, ("e:a",), "gap")
    value = ValueAssessment(
        delta_scientific_capability="SUBSTANTIAL", delta_engineering_capability="SUBSTANTIAL", delta_validation_capability="SUBSTANTIAL",
        delta_decision_capability="SUBSTANTIAL", delta_coverage="SUBSTANTIAL", delta_risk_reduction="SUBSTANTIAL", delta_coordination="SUBSTANTIAL",
        delta_speed="SUBSTANTIAL", delta_robustness="SUBSTANTIAL", delta_complexity="LOW", delta_coordination_cost="LOW", delta_failure_surface="LOW",
        delta_maintenance_cost="LOW", delta_duplication_risk="LOW", delta_security_surface="LOW", net_value_judgement="POSITIVE",
        rationale="material gap", evidence_refs=("e:value",),
    )
    centrality = {"downstream_dependencies": 1, "tasks_enabled": 2, "scientific_importance": "HIGH", "risk_reduction": "HIGH", "validation_importance": "HIGH", "cross_mission_relevance": "HIGH", "frequency_of_required_use": "RECURRING", "irreversibility_if_missing": "HIGH", "decision_impact": "HIGH"}
    return MissionAdmissionProposal("PROP-RUNTIME", "X", "Persistent capability is required.", ("capability",), (fit,), "No existing mission is sufficient.", "Collaboration is persistently discontinuous.", "NEW-RUNTIME", ("capability",), ("unrelated work",), value, "LOW", ("mission registry",), "least privilege", "preserve provenance", "provider-neutral", ("zero-context",), ("retire when value disappears",), centrality=centrality)


def _decision():
    proposal = _proposal()
    return MissionEvolutionEngine([{"mission_id": "A", "canonical_name": "A", "mission_type": "TEST", "status": "ACTIVE"}]).decide(
        action_x="X", necessity=True, fits=proposal.current_missions_audited, collaboration_sufficient=False, temporary_task_force_sufficient=False,
        coherence=True, integrability=True, validatability=True, marginal_value=proposal.expected_marginal_value,
        centrality=proposal.centrality, proposal=proposal)


def _runtime(tmp_path):
    missions = tmp_path / "docs" / "missions"
    missions.mkdir(parents=True)
    (missions / "MISSION_REGISTRY.json").write_text(json.dumps({"missions": [{"mission_id": "A", "canonical_name": "A", "mission_type": "TEST", "status": "ACTIVE"}]}), encoding="utf-8")
    return MissionEvolutionRuntime(tmp_path)


def test_admission_is_persisted_and_discoverable(tmp_path):
    runtime = _runtime(tmp_path)
    decision = _decision()
    assert runtime.stage_admission(decision, {"CAN_AUTHORIZE": True}).exists()
    runtime.commit_staged("PROP-RUNTIME", {"CAN_AUTHORIZE": True})
    result = runtime.validate_zero_context("NEW-RUNTIME")
    assert result["passed"] is True
    assert result["next"].startswith("LOAD_CONTRACT")


def test_stale_admission_fails_closed(tmp_path):
    runtime = _runtime(tmp_path)
    runtime.stage_admission(_decision(), {"CAN_AUTHORIZE": True})
    (runtime.missions_root / "MISSION_REGISTRY.VERSION").write_text("different-version", encoding="utf-8")
    try:
        runtime.commit_staged("PROP-RUNTIME", {"CAN_AUTHORIZE": True})
    except EvolutionRuntimeError as exc:
        assert "STALE_REGISTRY_VERSION" in str(exc)
    else:
        raise AssertionError("stale admission must fail closed")
