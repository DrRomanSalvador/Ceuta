import json
from pathlib import Path

from app.missions.evolution import (
    EvolutionEvidence,
    EvidenceLevel,
    MissionAdmissionProposal,
    MissionEvolutionEngine,
    MissionFit,
    ValueAssessment,
)

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_proposal(raw):
    fits = tuple(MissionFit(**{**item, "evidence_refs": tuple(item.get("evidence_refs", ()))}) for item in raw["current_missions_audited"])
    value_raw = raw["expected_marginal_value"]
    value = ValueAssessment(**{**value_raw, "evidence_refs": tuple(value_raw.get("evidence_refs", ()))})
    evidence = tuple(EvolutionEvidence(**{**item, "level": EvidenceLevel(item["level"]), "source_refs": tuple(item.get("source_refs", ()))}) for item in raw["evidence"])
    return MissionAdmissionProposal(
        proposal_id=raw["proposal_id"], action_x=raw["action_x"], problem_statement=raw["problem_statement"],
        required_capability=tuple(raw["required_capability"]), current_missions_audited=fits,
        why_existing_missions_are_insufficient=raw["why_existing_missions_are_insufficient"],
        why_collaboration_is_insufficient=raw["why_collaboration_is_insufficient"],
        proposed_mission_id=raw["proposed_mission_id"], proposed_scope=tuple(raw["proposed_scope"]),
        non_scope=tuple(raw["non_scope"]), expected_marginal_value=value,
        expected_complexity_cost=raw["expected_complexity_cost"], dependencies=tuple(raw["dependencies"]),
        security_implications=raw["security_implications"], scientific_implications=raw["scientific_implications"],
        operational_implications=raw["operational_implications"], validation_plan=tuple(raw["validation_plan"]),
        retirement_plan=tuple(raw["retirement_plan"]), evidence=evidence, centrality=raw["centrality"],
    )


def decide_founder(proposal, registry):
    return MissionEvolutionEngine(registry).decide(
        action_x=proposal.action_x,
        necessity=True,
        fits=proposal.current_missions_audited,
        collaboration_sufficient=False,
        temporary_task_force_sufficient=False,
        coherence=True,
        integrability=True,
        validatability=True,
        marginal_value=proposal.expected_marginal_value,
        centrality=proposal.centrality,
        proposal=proposal,
    )


def test_engine_admits_founder_only_after_all_gates_and_authority():
    registry = load_json(ROOT / "docs/missions/MISSION_REGISTRY.json")["missions"]
    proposal = build_proposal(load_json(ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json"))
    engine = MissionEvolutionEngine(registry)
    decision = decide_founder(proposal, registry)
    assert decision.admitted is True
    engine.authorize(decision, {"CAN_AUTHORIZE": True})


def test_committed_founder_contract_and_registry_entry_match_engine_output():
    registry = load_json(ROOT / "docs/missions/MISSION_REGISTRY.json")["missions"]
    proposal = build_proposal(load_json(ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json"))
    engine = MissionEvolutionEngine(registry)
    decision = decide_founder(proposal, registry)
    assert decision.decision == "ADMIT"
    assert engine.generate_contract(proposal) == load_json(ROOT / "docs/missions/founder/INVOCATION_CONTRACT.json")
    generated_registration = engine.generate_registration_entry(proposal)
    committed_registration = next(m for m in registry if m["mission_id"] == "FOUNDER")
    assert generated_registration == committed_registration


def test_non_redundancy_gate_rejects_a_materially_sufficient_existing_mission():
    registry = load_json(ROOT / "docs/missions/MISSION_REGISTRY.json")["missions"]
    proposal = build_proposal(load_json(ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json"))
    fits = list(proposal.current_missions_audited)
    original = fits[0]
    fits[0] = MissionFit(
        mission_id=original.mission_id, capability_match="SUFFICIENT", domain_match=original.domain_match,
        method_match=original.method_match, authority_match=original.authority_match, temporal_match=original.temporal_match,
        scale_match=original.scale_match, scientific_match=original.scientific_match, operational_match="SUFFICIENT",
        available_now=True, can_extend_without_new_mission=original.can_extend_without_new_mission,
        evidence_refs=original.evidence_refs, rationale=original.rationale,
    )
    decision = MissionEvolutionEngine(registry).decide(
        action_x=proposal.action_x, necessity=True, fits=fits, collaboration_sufficient=False,
        temporary_task_force_sufficient=False, coherence=True, integrability=True, validatability=True,
        marginal_value=proposal.expected_marginal_value, centrality=proposal.centrality, proposal=proposal,
    )
    assert decision.decision == "DO_NOT_CREATE"
    assert "NON_REDUNDANCY" in decision.failed_gates
