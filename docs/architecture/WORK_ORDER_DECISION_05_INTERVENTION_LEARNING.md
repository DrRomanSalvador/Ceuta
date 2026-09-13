# Decision-system work order 05 — Intervention, response and learning

## Objective
Close the decision loop so interventions become auditable experiments and observed responses update future inference without contaminating evidence.

## Required implementation
- Explicit intervention identity, target, timing, dose/intensity, intended mechanism and constraints.
- Distinguish planned intervention from delivered intervention and actual exposure.
- Measure response against pre-specified outcomes and counterfactual/reference trajectory where identifiable.
- Detect adverse, unintended and interaction effects.
- Handle interference, spillovers and simultaneous interventions.
- Prevent post-intervention information from leaking into the pre-intervention decision record.
- Create prospective prediction/outcome pairs and update model performance only from temporally valid outcomes.
- Champion/challenger lifecycle with shadow evaluation, promotion, retirement and rollback criteria.
- Preserve failed interventions, failed hypotheses and negative results as reusable epistemic memory.
- Detect model degradation, distribution shift and intervention-induced observation-process changes.

## Acceptance criteria
Every intervention must produce a machine-readable response record linked to the originating decision and information set; learning must be prospective, versioned and auditable, and model promotion must require explicit performance evidence.
