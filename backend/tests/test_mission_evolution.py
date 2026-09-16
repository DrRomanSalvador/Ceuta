from app.missions.evolution import (
    EvidenceLevel,
    EvolutionEvidence,
    MissionAdmissionProposal,
    MissionEvolutionEngine,
    MissionFit,
    ValueAssessment,
    EvolutionError,
)


REGISTRY = [
    {"mission_id": "A", "canonical_name": "A", "mission_type": "TEST", "status": "ACTIVE"},
    {"mission_id": "B", "canonical_name": "B", "mission_type": "TEST", "status": "ACTIVE"},
]


def value(judgement: str = "POSITIVE") -> ValueAssessment:
    return ValueAssessment(
        delta_scientific_capability="SUBSTANTIAL",
        delta_engineering_capability="LOW",
        delta_validation_capability="SUBSTANTIAL",
        delta_decision_capability="MODERATE",
        delta_coverage="SUBSTANTIAL",
        delta_risk_reduction="SUBSTANTIAL",
        delta_coordination="MODERATE",
        delta_speed="MODERATE",
        delta_robustness="SUBSTANTIAL",
        delta_complexity="LOW",
        delta_coordination_cost="LOW",
        delta_failure_surface="LOW",
        delta_maintenance_cost="LOW",
        delta_duplication_risk="LOW",
        delta_security_surface="LOW",
        net_value_judgement=judgement,
        rationale="The new capability closes a persistent material gap without duplicating an existing mandate.",
        evidence_refs=("evidence:value",),
    )


def fit(**overrides):
    base = dict(
        mission_id="A",
        capability_match="INSUFFICIENT",
        domain_match="PARTIAL",
        method_match="INSUFFICIENT",
        authority_match="INSUFFICIENT",
        temporal_match="SUFFICIENT",
        scale_match="SUFFICIENT",
        scientific_match="PARTIAL",
        operational_match="INSUFFICIENT",
        available_now=True,
        can_extend_without_new_mission=False,
        evidence_refs=("evidence:a",),
        rationale="Material authority and capability gap.",
    )
    base.update(overrides)
    return MissionFit(**base)


def proposal() -> MissionAdmissionProposal:
    return MissionAdmissionProposal(
        proposal_id="PROP-001",
        action_x="Perform a permanent cross-domain capability absent from the current control plane.",
        problem_statement="A persistent operational capability is required.",
        required_capability=("cross-domain analysis",),
        current_missions_audited=(fit(),),
        why_existing_missions_are_insufficient="No current mission has sufficient authority and method fit.",
        why_collaboration_is_insufficient="Repeated handoffs create a persistent capability discontinuity.",
        proposed_mission_id="NEW-MISSION",
        proposed_scope=("the declared cross-domain capability",),
        non_scope=("unrelated domain expansion",),
        expected_marginal_value=value(),
        expected_complexity_cost="LOW",
        dependencies=("mission registry",),
        security_implications="Least privilege; no undeclared writes.",
        scientific_implications="Validation must preserve provenance.",
        operational_implications="Must support provider-agnostic task handoffs.",
        validation_plan=("zero-context discovery", "authority isolation", "concurrency conflict test"),
        retirement_plan=("retire if repeated lifecycle review shows no material value",),
        evidence=(EvolutionEvidence("e1", "Persistent gap", EvidenceLevel.OBSERVED, ("source:1",), "Observed in repeated tasks."),),
        centrality={"downstream_dependencies": 3, "tasks_enabled": 5, "irreversibility_if_missing": "HIGH"},
    )


def test_existing_capability_wins_over_new_mission():
    engine = MissionEvolutionEngine(REGISTRY)
    decision = engine.decide(
        action_x="X",
        necessity=True,
        fits=(fit(capability_match="SUFFICIENT", authority_match="SUFFICIENT", operational_match="SUFFICIENT"),),
        collaboration_sufficient=False,
        temporary_task_force_sufficient=False,
        coherence=True,
        integrability=True,
        validatability=True,
        marginal_value=value(),
        centrality={"tasks_enabled": 10},
        proposal=proposal(),
    )
    assert decision.decision == "DO_NOT_CREATE"
    assert decision.precedence_path == ("EXISTING_CAPABILITY",)


def test_extension_precedes_collaboration_and_creation():
    engine = MissionEvolutionEngine(REGISTRY)
    decision = engine.decide(
        action_x="X",
        necessity=True,
        fits=(fit(can_extend_without_new_mission=True),),
        collaboration_sufficient=True,
        temporary_task_force_sufficient=True,
        coherence=True,
        integrability=True,
        validatability=True,
        marginal_value=value(),
        centrality={},
        proposal=proposal(),
    )
    assert decision.decision == "EXTEND_EXISTING_MISSION"


def test_collaboration_precedes_temporary_task_force_and_creation():
    engine = MissionEvolutionEngine(REGISTRY)
    decision = engine.decide(
        action_x="X",
        necessity=True,
        fits=(fit(),),
        collaboration_sufficient=True,
        temporary_task_force_sufficient=True,
        coherence=True,
        integrability=True,
        validatability=True,
        marginal_value=value(),
        centrality={},
        proposal=proposal(),
    )
    assert decision.decision == "USE_CROSS_MISSION_COLLABORATION"


def test_failed_gate_blocks_creation():
    engine = MissionEvolutionEngine(REGISTRY)
    decision = engine.decide(
        action_x="X",
        necessity=True,
        fits=(fit(),),
        collaboration_sufficient=False,
        temporary_task_force_sufficient=False,
        coherence=True,
        integrability=True,
        validatability=True,
        marginal_value=value("NEGATIVE"),
        centrality={},
        proposal=proposal(),
    )
    assert decision.decision == "DO_NOT_CREATE"
    assert "MARGINAL_VALUE" in decision.failed_gates


def test_all_gates_produce_admission_but_authority_is_separate():
    engine = MissionEvolutionEngine(REGISTRY)
    decision = engine.decide(
        action_x="X",
        necessity=True,
        fits=(fit(),),
        collaboration_sufficient=False,
        temporary_task_force_sufficient=False,
        coherence=True,
        integrability=True,
        validatability=True,
        marginal_value=value(),
        centrality={"tasks_enabled": 5},
        proposal=proposal(),
    )
    assert decision.admitted
    try:
        engine.authorize(decision, {"CAN_AUTHORIZE": False})
    except EvolutionError as exc:
        assert "CAN_AUTHORIZE" in str(exc)
    else:
        raise AssertionError("Admission must not bypass authorization")


def test_contract_and_prompt_are_generated_from_admitted_proposal():
    p = proposal()
    contract = MissionEvolutionEngine.generate_contract(p)
    prompt = MissionEvolutionEngine.generate_canonical_prompt(p)
    assert contract["mission_id"] == p.proposed_mission_id
    assert "MISSION IDENTITY" in prompt
    assert "MISSION FAILURE RECOVERY" in prompt
    assert "conversation" in prompt.lower()
