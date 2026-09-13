"""Prevents unsupported epistemic upgrades across the decision loop."""
from dataclasses import dataclass
from enum import IntEnum
from ..errors import ContractViolation

class EvidenceLevel(IntEnum):
    OBSERVED=0; ESTIMATED=1; ASSOCIATIONAL=2; HYPOTHETICAL=3; CAUSAL=4; PREDICTIVE=5; DECISIONAL=6; INTERVENTIONAL=7

@dataclass(frozen=True, slots=True)
class EpistemicClaim:
    claim_id: str
    level: EvidenceLevel
    basis_ids: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    def __post_init__(self):
        if not self.claim_id or not self.basis_ids: raise ContractViolation("claim and basis required")

class EpistemicIntegrity:
    @staticmethod
    def can_upgrade(source: EvidenceLevel, target: EvidenceLevel, explicit_justification: bool) -> bool:
        return target.value <= source.value or explicit_justification

    @staticmethod
    def require(source: EvidenceLevel, target: EvidenceLevel, justification: str | None = None) -> None:
        if target.value > source.value and not justification:
            raise ContractViolation("epistemic upgrade requires explicit justification")
