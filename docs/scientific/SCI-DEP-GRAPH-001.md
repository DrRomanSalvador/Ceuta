# SCI-DEP-GRAPH-001 — Scientific Dependency & Data-Generating-Process Graph

**Status:** IMPLEMENTED — NOT YET VALIDATED
**Priority:** P0
**Branch:** `scientific-dependency-semantics`
**Base:** `main@80fa872c95bab5af5ed279c42774173bc7a52652`
**Head:** `00c525bd42f1b45cc73eff5250c2a0db80ac17c8`
**PR:** #31

## Scientific problem
The existing semantic graph already separated association, temporal precedence, source dependency and causal hypotheses, but it did not expose enough explicit edge semantics for the full data-generating chain. In particular, prediction, observation, reporting, acquisition, revision and intervention processes could not be represented as first-class relation types.

Collapsing these relations risks treating computational dependency, predictive association and causal mechanism as the same scientific object.

## Scientific requirement
Represent at minimum:

- observation and measurement processes;
- derivation/dependency;
- association;
- prediction;
- temporal precedence;
- causal hypothesis and causal support;
- reporting/publication;
- acquisition;
- revision;
- intervention;
- modification/conditioning/confounding;
- feedback.

`PREDICTS` MUST NOT imply `CAUSES`.
`DEPENDS_ON` MUST NOT imply `CAUSES`.
Temporal precedence MUST NOT imply causality.

## Current implementation
`backend/app/core/epistemology_p0/advanced/semantic_graph.py` now contains explicit `EdgeKind` values for:

`OBSERVES`, `PREDICTS`, `REPORTED_BY`, `ACQUIRED_BY`, `REVISED_BY`, `INTERVENED_ON_BY`, `MODIFIES`, `CONDITIONS`, `CONFOUNDS`, `FEEDS_BACK_TO`.

Point-in-time process edges require explicit scientific identity fields. `PREDICTS` rejects an embedded `causality_claim=true` and therefore cannot silently upgrade a predictive relation into a causal claim.

The prediction edge contract was reconciled against SERPIENTE `Forecast`: it requires `prediction_id`, `origin_time`, and `horizon`, rather than inventing a `target_time` field absent from the producer contract.

## Mathematical consequence
The project can now preserve separate graph layers conceptually:

- `G_obs`: observation / measurement / data-generating relations;
- `G_pred`: predictive relations;
- `G_causal`: causal hypotheses and identified causal relations;
- `G_feedback`: intervention/response feedback relations.

No causal interpretation is inferred from membership in `G_obs` or `G_pred`.

## Data contract
Every process-sensitive edge must carry an identity that can be traced to a durable artifact:

- observation → `observation_id`;
- prediction → `prediction_id`, `origin_time`, `horizon`;
- reporting → `reporting_process_id`;
- acquisition → `acquisition_process_id`;
- revision → `revision_id`;
- intervention → `intervention_id`.

Temporal context and provenance remain external properties of the participating evidence/process nodes and must be preserved through replay.

## Validation required
1. Full semantic-graph test suite passes.
2. Existing causal safeguards remain unchanged.
3. Predictive edges cannot encode causal claims.
4. Point-in-time process relations fail closed when their identity is absent.
5. Replay/temporal consumers preserve the distinction between observation time and availability/revision time.
6. Cross-domain consumers do not infer causal status from `PREDICTS`, `DEPENDS_ON`, or `TEMPORAL_PRECEDENCE`.

## Failure condition
Any runtime path that upgrades:

`association → causality`

or

`prediction → causality`

or

`temporal precedence → causality`

without an explicit causal identification assessment is scientifically invalid.

## Remaining uncertainty
The graph ontology is now richer, but mechanism identifiability is not solved by adding edge types. Competing hypotheses, assumptions, evidence, intervention information and falsification tests remain necessary for causal identification.

The current repository does not yet provide an independently recorded validation run for PR #31. GitHub Actions exposes no PR-triggered run for the current head, and the repository CI workflow is configured for manual dispatch only.

## Checkpoint
- Repository inspected: current `main` at `80fa872c95bab5af5ed279c42774173bc7a52652`.
- Existing temporal implementation verified in `epistemology_p0/temporal/multitemporal.py`.
- Existing semantic graph and causal contracts inspected.
- SERPIENTE `Observation` and `Forecast` contracts inspected; both enforce timezone-aware temporal semantics, and `Forecast` uses `origin_time` + `horizon`.
- Implementation, regression tests and scientific handoff/checkpoint were committed on the scientific branch.
- PR #31 opened against current `main`.
- `fetch_commit_workflow_runs` for the branch head returned no runs.
