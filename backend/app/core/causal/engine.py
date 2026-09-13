"""End-to-end causal assessment gate used by decision intelligence."""
from __future__ import annotations

from .contracts import CausalAssessment, CausalEvidence, CausalHypothesis
from .falsification import FalsificationEngine
from .graph import CausalGraph
from .identification import CausalIdentifier


class CausalInferenceEngine:
    def __init__(self) -> None:
        self.identifier = CausalIdentifier()
        self.falsifier = FalsificationEngine()

    def assess(
        self,
        graph: CausalGraph,
        hypothesis: CausalHypothesis,
        evidence: tuple[CausalEvidence, ...] = (),
        competing_hypotheses: tuple[str, ...] = (),
    ) -> CausalAssessment:
        identification = self.identifier.assess(graph, hypothesis)
        falsification = self.falsifier.evaluate(hypothesis, evidence)
        residual = list(identification.blockers)
        residual.extend(falsification.unresolved_tests)
        if falsification.failed_tests:
            residual.extend(falsification.failed_tests)
        return CausalAssessment(
            hypothesis=hypothesis,
            identification=identification,
            evidence=evidence,
            competing_hypotheses=competing_hypotheses,
            residual_uncertainty=tuple(dict.fromkeys(residual)),
            interaction_terms={f"{hypothesis.exposure}*{hypothesis.outcome}": "candidate_interaction"},
        )
