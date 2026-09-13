# Canonical State and Trajectory Substrate

## Purpose

CeutIA must reason about systems as evolving configurations rather than isolated events. This layer makes that temporal object explicit before forecasting, causal interpretation, intervention, or decision logic consumes it.

The substrate is domain-agnostic. It does not define health variables, territorial variables, economic variables, or any other specialist ontology.

## Core object

A `SystemStateContract` is a time-indexed, provenance-aware snapshot containing domains, variable states, observed interactions, and explicit non-causal interaction effects.

A `StateSnapshot` adds:

- lineage to the state that generated it;
- observation and evidence identifiers;
- model identifiers used to construct the state;
- uncertainty components that retain their kind and basis rather than being collapsed into an unexplained score.

A `StateTrajectory` is an append-only sequence of snapshots. It rejects duplicate state identifiers, time reversal, and broken parentage.

## Transition semantics

A `StateTransition` records what changed between adjacent states:

`state(t) -> observed transition -> state(t+1)`

It records added observations and changed variables. It does **not** infer causality. Temporal succession is evidence about sequence, not proof of mechanism.

## Scientific boundary

This substrate deliberately does not claim:

- that a state is a latent-state estimate merely because it is structured;
- that an interaction is causal;
- that uncertainty components can be summed without a justified statistical model;
- that a detected transition is a regime change;
- that a state margin is a probability of failure;
- that a trajectory is a forecast.

Those claims require separate, validated methods and evidence.

## Reproducibility

Every snapshot can be traced through:

`state_id -> parent_state_id -> observation_ids -> evidence_ids -> model_ids`

This provides the minimum lineage needed to reconstruct why a state existed at a particular point in the trajectory. Downstream layers must preserve this lineage when producing forecasts, causal analyses, interventions, and decisions.

## Next scientific increments

The next bounded increments should build on this substrate rather than create parallel state representations:

1. latent-state estimation with explicit observation models;
2. dynamic regimes and change-point inference;
3. capacity/reserve and recovery metrics with domain-specific semantics;
4. trajectory-level early-warning statistics with uncertainty and false-positive controls;
5. prospective falsification and model-learning records.

Each increment requires deterministic tests, an executable verifier, documentation, a checkpoint commit, and CI validation before closure.
