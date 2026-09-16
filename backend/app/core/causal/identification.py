"""Identification gates: association alone can never authorize a causal claim.

The identifier separates three different questions that must not be conflated:

1. identification of the requested causal estimand under the declared graph and
   assumptions;
2. falsification/diagnostic evidence (for example negative controls); and
3. transportability/generalisation to a target population or regime.

Negative controls and transportability are therefore not treated as universal
logical prerequisites for *internal* identification. They remain explicit
requirements/limitations when the hypothesis claims them.
"""
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

        # Transportability is a separate target claim. It should block a claim
        # of transported effect, but not the identification of an internally
        # defined effect in the declared source population.
        if hypothesis.transportability_addressed is False and hypothesis.population:
            assumptions.append("transportability_not_established")

        identified = not blockers
        falsification_tests = tuple(
            f"negative_control:{name}" for name in hypothesis.negative_controls
        )
        if not falsification_tests:
            assumptions.append("negative_control_tests_not_declared")

        return IdentificationAssessment(
            hypothesis_id=hypothesis.hypothesis_id,
            identified=identified,
            estimand=hypothesis.estimand,
            adjustment_set=tuple(sorted(declared)),
            blockers=tuple(blockers),
            assumptions=tuple(assumptions),
            falsification_tests=falsification_tests,
        )
