import json
import shutil
from pathlib import Path

import pytest

from app.missions.evolution import EvolutionEvidence, EvidenceLevel, MissionAdmissionProposal, MissionEvolutionEngine, MissionFit, ValueAssessment
from app.missions.evolution_runtime import EvolutionRuntimeError, MissionEvolutionRuntime

ROOT = Path(__file__).resolve().parents[1]


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _proposal(raw):
    fits = tuple(MissionFit(**{**item, "evidence_refs": tuple(item.get("evidence_refs", ()))}) for item in raw["current_missions_audited"])
    value_raw = raw["expected_marginal_value"]
    value = ValueAssessment(**{**value_raw, "evidence_refs": tuple(value_raw.get("evidence_refs", ()))})
    evidence = tuple(EvolutionEvidence(**{**item, "level": EvidenceLevel(item["level"]), "source_refs": tuple(item.get("source_refs", ()))}) for item in raw["evidence"])
    return MissionAdmissionProposal(
        proposal_id=raw["proposal_id"], action_x=raw["action_x"], problem_statement=raw["problem_statement"],
        required_capability=tuple(raw["required_capability"]), current_missions_audited=fits,
        why_existing_missions_are_insufficient=raw["why_existing_missions_are_insufficient"],
        why_collaboration_is_insufficient=raw["why_collaboration_is_insufficient"], proposed_mission_id=raw["proposed_mission_id"],
        proposed_scope=tuple(raw["proposed_scope"]), non_scope=tuple(raw["non_scope"]), expected_marginal_value=value,
        expected_complexity_cost=raw["expected_complexity_cost"], dependencies=tuple(raw["dependencies"]),
        security_implications=raw["security_implications"], scientific_implications=raw["scientific_implications"],
        operational_implications=raw["operational_implications"], validation_plan=tuple(raw["validation_plan"]),
        retirement_plan=tuple(raw["retirement_plan"]), evidence=evidence, centrality=raw["centrality"],
    )


def _decision(proposal, registry):
    return MissionEvolutionEngine(registry).decide(
        action_x=proposal.action_x, necessity=True, fits=proposal.current_missions_audited,
        collaboration_sufficient=False, temporary_task_force_sufficient=False,
        coherence=True, integrability=True, validatability=True,
        marginal_value=proposal.expected_marginal_value, centrality=proposal.centrality, proposal=proposal,
    )


def test_founder_zero_context_discovery_uses_canonical_registry_and_state():
    result = MissionEvolutionRuntime(ROOT).validate_zero_context("FOUNDER")
    assert result["passed"] is True
    assert result["mission_id"] == "FOUNDER"
    assert result["contract_exists"] is True
    assert result["state_exists"] is True


def test_founder_admission_runtime_can_replay_transaction_without_mutating_real_registry(tmp_path):
    registry = _load(ROOT / "docs/missions/MISSION_REGISTRY.json")
    registry["missions"] = [m for m in registry["missions"] if m.get("mission_id") != "FOUNDER"]
    missions_root = tmp_path / "docs" / "missions"
    missions_root.mkdir(parents=True)
    (missions_root / "MISSION_REGISTRY.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    shutil.copytree(ROOT / "docs/missions/evolution", missions_root / "evolution")
    proposal = _proposal(_load(ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json"))
    decision = _decision(proposal, registry["missions"])
    assert decision.decision == "ADMIT"
    runtime = MissionEvolutionRuntime(tmp_path)
    staged = runtime.stage_admission(decision, {"CAN_AUTHORIZE": True})
    assert staged.exists()
    committed = runtime.commit_staged(proposal.proposal_id, {"CAN_AUTHORIZE": True})
    assert committed["status"] == "COMMITTED"
    assert (missions_root / "founder" / "INVOCATION_CONTRACT.json").exists()
    assert (missions_root / "founder" / "MISSION_STATE.json").exists()
    assert (missions_root / "founder" / "CANONICAL_MISSION_PROMPT.md").exists()


def test_founder_runtime_rejects_stale_registry_transaction(tmp_path):
    registry = _load(ROOT / "docs/missions/MISSION_REGISTRY.json")
    registry["missions"] = [m for m in registry["missions"] if m.get("mission_id") != "FOUNDER"]
    missions_root = tmp_path / "docs" / "missions"
    missions_root.mkdir(parents=True)
    registry_path = missions_root / "MISSION_REGISTRY.json"
    registry_path.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    (missions_root / "evolution" / "transactions").mkdir(parents=True)
    proposal = _proposal(_load(ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json"))
    decision = _decision(proposal, registry["missions"])
    runtime = MissionEvolutionRuntime(tmp_path)
    runtime.stage_admission(decision, {"CAN_AUTHORIZE": True})
    mutated = _load(registry_path)
    mutated["status"] = "MUTATED_AFTER_STAGE"
    registry_path.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(EvolutionRuntimeError, match="STALE_REGISTRY_VERSION"):
        runtime.commit_staged(proposal.proposal_id, {"CAN_AUTHORIZE": True})
