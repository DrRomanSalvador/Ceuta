from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class EvolutionError(ValueError):
    """Raised when a mission-evolution operation cannot be completed safely."""


class EvidenceLevel(str, Enum):
    OBSERVED = "OBSERVED"
    HIGHLY_REPLICATED = "HIGHLY_REPLICATED"
    INFERRED = "INFERRED"
    HYPOTHESIS = "HYPOTHESIS"
    NOT_DETERMINABLE = "NOT_DETERMINABLE"
    CONTRADICTION = "CONTRADICTION"


@dataclass(frozen=True, slots=True)
class MissionFit:
    mission_id: str
    capability_match: str
    domain_match: str
    method_match: str
    authority_match: str
    temporal_match: str
    scale_match: str
    scientific_match: str
    operational_match: str
    available_now: bool
    can_extend_without_new_mission: bool
    evidence_refs: tuple[str, ...] = ()
    rationale: str = ""

    @property
    def materially_sufficient(self) -> bool:
        return self.available_now and self.capability_match.upper() == "SUFFICIENT" and self.authority_match.upper() == "SUFFICIENT" and self.operational_match.upper() == "SUFFICIENT"


@dataclass(frozen=True, slots=True)
class ValueAssessment:
    delta_scientific_capability: str
    delta_engineering_capability: str
    delta_validation_capability: str
    delta_decision_capability: str
    delta_coverage: str
    delta_risk_reduction: str
    delta_coordination: str
    delta_speed: str
    delta_robustness: str
    delta_complexity: str
    delta_coordination_cost: str
    delta_failure_surface: str
    delta_maintenance_cost: str
    delta_duplication_risk: str
    delta_security_surface: str
    net_value_judgement: str
    rationale: str
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EvolutionEvidence:
    evidence_id: str
    claim: str
    level: EvidenceLevel
    source_refs: tuple[str, ...]
    observation: str
    limitations: str = ""


@dataclass(frozen=True, slots=True)
class MissionAdmissionProposal:
    proposal_id: str
    action_x: str
    problem_statement: str
    required_capability: tuple[str, ...]
    current_missions_audited: tuple[MissionFit, ...]
    why_existing_missions_are_insufficient: str
    why_collaboration_is_insufficient: str
    proposed_mission_id: str
    proposed_scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    expected_marginal_value: ValueAssessment
    expected_complexity_cost: str
    dependencies: tuple[str, ...]
    security_implications: str
    scientific_implications: str
    operational_implications: str
    validation_plan: tuple[str, ...]
    retirement_plan: tuple[str, ...]
    evidence: tuple[EvolutionEvidence, ...] = ()
    centrality: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    decision: str
    reasons: tuple[str, ...]
    failed_gates: tuple[str, ...]
    precedence_path: tuple[str, ...]
    proposal: MissionAdmissionProposal | None = None

    @property
    def admitted(self) -> bool:
        return self.decision == "ADMIT"


class MissionEvolutionEngine:
    """Control-plane decision engine for admitting, extending, or rejecting missions."""

    REQUIRED_GATES = ("NECESSITY", "NON_REDUNDANCY", "MARGINAL_VALUE", "COHERENCE", "INTEGRABILITY", "VALIDATABILITY")
    CENTRALITY_FIELDS = (
        "downstream_dependencies", "tasks_enabled", "scientific_importance", "risk_reduction",
        "validation_importance", "cross_mission_relevance", "frequency_of_required_use",
        "irreversibility_if_missing", "decision_impact",
    )
    PRECEDENCE = ("EXISTING_CAPABILITY", "EXISTING_MISSION_EXTENSION", "CROSS_MISSION_COLLABORATION", "TEMPORARY_TASK_FORCE", "NEW_MISSION")

    def __init__(self, registry: Sequence[Mapping[str, Any]]) -> None:
        self.registry = tuple(dict(m) for m in registry)

    def audit_missions(self, fits: Sequence[MissionFit]) -> tuple[MissionFit, ...]:
        known = {m.get("mission_id") for m in self.registry}
        unknown = [fit.mission_id for fit in fits if fit.mission_id not in known]
        if unknown:
            raise EvolutionError(f"Mission audit contains unknown mission IDs: {unknown}")
        return tuple(fits)

    @classmethod
    def assess_centrality(cls, centrality: Mapping[str, Any]) -> dict[str, Any]:
        missing = [field for field in cls.CENTRALITY_FIELDS if field not in centrality]
        if missing:
            raise EvolutionError(f"Centrality assessment is incomplete: missing {missing}")
        result = dict(centrality)
        result["assessment_status"] = "EXPLICIT"
        return result

    @staticmethod
    def assess_marginal_value(value: ValueAssessment) -> ValueAssessment:
        if not value.rationale.strip() or not value.evidence_refs:
            raise EvolutionError("Marginal-value assessment requires rationale and evidence references")
        if value.net_value_judgement.upper() not in {"POSITIVE", "NEGATIVE", "UNCERTAIN"}:
            raise EvolutionError("net_value_judgement must be POSITIVE, NEGATIVE or UNCERTAIN")
        return value

    def decide(self, *, action_x: str, necessity: bool, fits: Sequence[MissionFit], collaboration_sufficient: bool,
               temporary_task_force_sufficient: bool, coherence: bool, integrability: bool, validatability: bool,
               marginal_value: ValueAssessment, centrality: Mapping[str, Any], proposal: MissionAdmissionProposal | None = None) -> AdmissionDecision:
        if not action_x.strip():
            raise EvolutionError("ACTION_X must be concrete and non-empty")
        audited = self.audit_missions(fits)
        assessed_centrality = self.assess_centrality(centrality)
        assessed_value = self.assess_marginal_value(marginal_value)
        if any(fit.materially_sufficient for fit in audited):
            return AdmissionDecision("DO_NOT_CREATE", ("An existing mission can perform ACTION_X within its current mandate.",), ("NON_REDUNDANCY",), ("EXISTING_CAPABILITY",))
        if any(fit.can_extend_without_new_mission for fit in audited):
            return AdmissionDecision("EXTEND_EXISTING_MISSION", ("An existing mission can absorb ACTION_X without breaking its contract or boundary.",), ("NON_REDUNDANCY",), ("EXISTING_MISSION_EXTENSION",))
        if collaboration_sufficient:
            return AdmissionDecision("USE_CROSS_MISSION_COLLABORATION", ("Existing missions can solve ACTION_X through a stable handoff/collaboration path.",), ("NON_REDUNDANCY",), ("CROSS_MISSION_COLLABORATION",))
        if temporary_task_force_sufficient:
            return AdmissionDecision("USE_TEMPORARY_TASK_FORCE", ("The capability is temporary or composable and does not justify a permanent mission boundary.",), ("NECESSITY",), ("TEMPORARY_TASK_FORCE",))

        gates = {
            "NECESSITY": necessity,
            "NON_REDUNDANCY": not any(f.materially_sufficient or f.can_extend_without_new_mission for f in audited),
            "MARGINAL_VALUE": assessed_value.net_value_judgement.upper() == "POSITIVE",
            "COHERENCE": coherence,
            "INTEGRABILITY": integrability,
            "VALIDATABILITY": validatability,
        }
        failed = tuple(name for name in self.REQUIRED_GATES if not gates[name])
        if failed:
            return AdmissionDecision("DO_NOT_CREATE", tuple(f"Gate {name} is not satisfied." for name in failed), failed, ("NEW_MISSION",), proposal)
        if proposal is None:
            raise EvolutionError("A proposal is required when all admission gates pass")
        if proposal.centrality and dict(proposal.centrality) != assessed_centrality:
            raise EvolutionError("Proposal centrality does not match the assessed centrality")
        return AdmissionDecision("ADMIT", ("All six mandatory admission gates are satisfied with explicit evidence.",), (), ("NEW_MISSION",), proposal)

    @staticmethod
    def authorize(decision: AdmissionDecision, authority_context: Mapping[str, bool]) -> None:
        if not decision.admitted:
            raise EvolutionError(f"Cannot authorize non-admitted decision: {decision.decision}")
        if not authority_context.get("CAN_AUTHORIZE", False):
            raise EvolutionError("Mission admission requires CAN_AUTHORIZE")

    @staticmethod
    def generate_contract(proposal: MissionAdmissionProposal) -> dict[str, Any]:
        return {
            "mission_id": proposal.proposed_mission_id, "mission_name": proposal.proposed_mission_id,
            "mission_type": "ADMITTED_FROM_EVOLUTION_ENGINE", "purpose": proposal.problem_statement,
            "scope": list(proposal.proposed_scope), "non_scope": list(proposal.non_scope), "inputs": [], "outputs": [],
            "capabilities": list(proposal.required_capability), "limitations": ["Must remain within the approved proposal scope."],
            "owner": proposal.proposed_mission_id,
            "authority": {"CAN_DISCOVER": True, "CAN_INVOKE": True, "CAN_READ": True, "CAN_PROPOSE": True, "CAN_MODIFY": False, "CAN_VALIDATE": False, "CAN_AUTHORIZE": False},
            "read_permissions": [], "write_permissions": [], "validation_role": "Validate only through declared validation plan.",
            "handoff_in": [], "handoff_out": [], "dependencies": list(proposal.dependencies),
            "state_location": f"docs/missions/{proposal.proposed_mission_id.lower()}/MISSION_STATE.json",
            "evidence_location": f"docs/missions/{proposal.proposed_mission_id.lower()}/EVIDENCE.json",
            "invocation_contract": f"docs/missions/{proposal.proposed_mission_id.lower()}/INVOCATION_CONTRACT.json",
            "security_requirements": [proposal.security_implications], "adversarial_tests": list(proposal.validation_plan),
            "completion_criteria": ["All declared integration and validation tests pass."], "retirement_criteria": list(proposal.retirement_plan),
        }

    @staticmethod
    def generate_registration_entry(proposal: MissionAdmissionProposal) -> dict[str, Any]:
        contract = MissionEvolutionEngine.generate_contract(proposal)
        return {
            "mission_id": proposal.proposed_mission_id, "canonical_name": proposal.proposed_mission_id,
            "mission_type": contract["mission_type"], "purpose": proposal.problem_statement,
            "scope": list(proposal.proposed_scope), "non_scope": list(proposal.non_scope),
            "status": "ADMITTED_PENDING_VALIDATION", "contract": contract["invocation_contract"],
            "invocation_contract": contract["invocation_contract"], "state_location": contract["state_location"],
            "evidence_location": contract["evidence_location"], "adversarial_tests": contract["adversarial_tests"],
            "completion_criteria": contract["completion_criteria"], "retirement_criteria": contract["retirement_criteria"],
        }

    @staticmethod
    def generate_canonical_prompt(proposal: MissionAdmissionProposal) -> str:
        p = proposal
        return f"""# {p.proposed_mission_id} — CANONICAL MISSION PROMPT

## MISSION IDENTITY
MISSION_ID = {p.proposed_mission_id}

## MISSION PURPOSE
{p.problem_statement}

## MISSION SCOPE
{chr(10).join(f'- {x}' for x in p.proposed_scope)}

## MISSION NON-SCOPE
{chr(10).join(f'- {x}' for x in p.non_scope)}

## MISSION CAPABILITIES
{chr(10).join(f'- {x}' for x in p.required_capability)}

## MISSION INPUTS
Inputs are exactly those declared by the machine-readable invocation contract; undeclared inputs are not accepted as authority.

## MISSION OUTPUTS
Outputs are exactly those declared by the machine-readable invocation contract; generated text is not evidence.

## MISSION AUTHORITY
Authority is granted by the control plane, never inferred from the prompt. Never modify state outside the declared write permissions.

## MISSION LIMITATIONS
Stay inside the approved scope. Escalate capability gaps rather than silently expanding scope.

## MISSION EVIDENCE RULES
Maintain SOURCE → PASSAGE/OBJECT → OBSERVATION → PATTERN → INFERENCE → CONFIDENCE provenance. Never silently upgrade evidence.

## MISSION HANDOFF RULES
Exchange TASK, CLAIM, HANDOFF, EVIDENCE, STATE, RESULT and VALIDATION objects; do not require the originating conversation.

## MISSION SECURITY RULES
{p.security_implications}

## MISSION STATE
Persistent state is the source of operational continuity; conversational context is not.

## MISSION BOOTSTRAP
DISCOVER → LOAD CONTRACT → CHECK AUTHORITY → CHECK INPUTS → EXECUTE → VALIDATE → PERSIST DELTA → HANDOFF/CONTINUE.

## MISSION EXECUTION LOOP
Observe → execute declared capability → record evidence → produce result → validate → persist versioned delta → reconcile conflicts → continue or hand off.

## MISSION VALIDATION
{chr(10).join(f'- {x}' for x in p.validation_plan)}

## MISSION ADVERSARIAL TESTING
Test identity isolation, scope escape, authority escalation, provenance loss, stale writes, concurrent claims, prompt contamination and zero-context discovery.

## MISSION FAILURE RECOVERY
Fail closed on missing authority, missing inputs, provenance failure or state-version conflict. Emit a conflict/failure record rather than overwriting or inventing state.

## MISSION RETIREMENT
{chr(10).join(f'- {x}' for x in p.retirement_plan)}

This prompt is an execution specification, not evidence of the mission's existence. Existence is established only by the canonical registry and contract.
"""
