"""Identification gates: association alone can never authorize a causal claim."""
from __future__ import annotations

from .contracts import CausalHypothesis, IdentificationAssessment
from .graph import CausalGraph


class CausalIdentifier:
    def assess(self, graph: CausalGraph, hypothesis: CausalHypothesis) -> IdentificationAssessment:
        blockers: list[str] = []
        assumptions = list(hypothesis.assumptions)
        candidates = set(graph.backdoor_candidates(hypothesis.exposure, hypothesis.outcome))
        declared = set(hypothesis.assumed_confounders)

        if candidates - declared:
            blockers.append("unaddressed_backdoor_candidates")
        if not hypothesis.assumptions:
            blockers.append("causal_assumptions_not_declared")
        if not hypothesis.negative_controls:
            blockers.append("negative_controls_missing")
        if hypothesis.exposure not in graph.ancestors(hypothesis.outcome):
            blockers.append("no_directed_exposure_to_outcome_path")
        if not hypothesis.population:
            blockers.append("target_population_not_declared")
        if not hypothesis.time_zero:
            blockers.append("time_zero_not_declared")
        if not hypothesis.consistency_declared:
            blockers.append("consistency_not_declared")
        if not hypothesis.positivity_declared:
            blockers.append("positivity_not_declared")
        if not hypothesis.interference_addressed:
            blockers.append("interference_not_addressed")
        if not hypothesis.time_varying_confounding_addressed:
            blockers.append("time_varying_confounding_not_addressed")
        if not hypothesis.transportability_addressed:
            blockers.append("transportability_not_addressed")

        identified = not blockers
        return IdentificationAssessment(
            hypothesis_id=hypothesis.hypothesis_id,
            identified=identified,
            estimand=hypothesis.estimand,
            adjustment_set=tuple(sorted(declared)),
            blockers=tuple(blockers),
            assumptions=tuple(assumptions),
            falsification_tests=tuple(
                f"negative_control:{name}" for name in hypothesis.negative_controls
            ),
        )
