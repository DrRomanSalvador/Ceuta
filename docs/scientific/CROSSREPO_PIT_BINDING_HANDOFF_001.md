# CROSSREPO-PIT-BINDING-001 — Scientific Handoff

**Status:** OPEN / REQUIRED FOR SCIENTIFIC PIT INTEGRITY CLAIM
**Priority:** P0
**Mission:** CROSSREPO-ENDPOINT-001
**Affected system:** CeutIA + SERPIENTE

## Scientific finding

The current cross-repository lifecycle proves that a SERPIENTE forecast carries a timezone-aware `origin_time`, `available_at`, provenance, and `point_in_time_fingerprint`; the canonical payload is integrity-protected and replay rejects a forecast when its stored availability/origin is after the replay reference time.

It does **not** prove the stronger semantic statement:

`point_in_time_fingerprint == hash(exact information set actually used by the forecasting computation)`.

Current SERPIENTE `PointInTimeStore.fingerprint(as_of)` hashes the point-in-time visible observation history. `LongitudinalForecaster.forecast(...)` accepts the fingerprint as an argument while receiving an arbitrary feature frame `X`. There is currently no machine-checkable lineage edge proving that `X` was deterministically derived from that exact visible observation set.

Therefore a producer-supplied fingerprint is an **attestation**, not independent proof of information-set membership.

## Evidence

- SERPIENTE `Observation.known_at(as_of)` requires publication and acquisition visibility before `as_of`.
- SERPIENTE `PointInTimeStore.history_at(as_of)` filters by `known_at`, event time, revision and acquisition order, then `fingerprint(as_of)` hashes the visible history.
- SERPIENTE `LongitudinalForecaster.forecast(...)` accepts `point_in_time_fingerprint` separately from `X`.
- CeutIA canonical contract v1.1 requires the fingerprint and integrity hash but does not contain the underlying input manifest.
- CeutIA replay verifies persisted availability/origin and payload integrity, not semantic membership of the producer's model inputs.
- Current PR #30 CI run `35066018857` passes 38/38 targeted tests; this is functional evidence and does not close the semantic PIT question.

## Identifiability result

Let `H_t` be the canonical point-in-time visible observation set and `X_t` the exact feature input matrix used by the model.

Current system establishes, at best:

`hash(H_t) = f_t`

and transmits `f_t`.

It does not establish:

`X_t = phi(H_t)`

for a recorded deterministic transformation `phi`, nor does it expose sufficient metadata to independently reconstruct `X_t` from `H_t`.

Thus the following mechanisms remain observationally equivalent at the current boundary:

1. correct PIT feature derivation from `H_t`;
2. feature derivation from a subset/transformation of `H_t`;
3. feature derivation containing information unavailable at `t` while retaining a truthful-looking external fingerprint.

The receiver cannot distinguish these cases from v1.1 payload fields alone.

## Exact requirement

Before claiming **semantic point-in-time information-set integrity**, the system must bind the forecast computation to a reproducible input manifest.

Minimum representation:

- `information_set_as_of` — timezone-aware reference time;
- `observation_manifest_hash` — canonical hash of the exact eligible observations/features;
- `feature_manifest_hash` — canonical hash of the exact model input matrix or deterministic feature manifest;
- `derivation_method_id` + version;
- `derivation_configuration_hash`;
- `source/revision visibility rule`;
- `feature availability cutoff`;
- `input lineage refs` sufficient to reconstruct the transformation.

If this metadata cannot fit the v1.1 contract without ambiguity, do **not** overload an existing field. Introduce a versioned contract extension (e.g. v1.2) and fail closed for claims requiring semantic PIT proof when the extension is absent.

## Expected behaviour

### Valid

A forecast is PIT-semantically eligible only when:

`information_set_as_of <= origin_time`

and the persisted manifest deterministically identifies the exact eligible inputs used for inference.

### Reject / abstain

- feature manifest timestamp after origin;
- feature source/revision unavailable at origin;
- missing derivation identity;
- mismatch between declared and recomputed manifest hash;
- unknown transformation lineage;
- inability to reconstruct eligibility.

## Validation criterion

A falsification test must construct two forecasts with identical model metadata and target but different input provenance:

- Forecast A uses only observations visible at `t`;
- Forecast B injects one observation acquired/published after `t`.

The system must produce distinguishable manifests and must reject B as PIT-ineligible. A third test must mutate the input manifest after persistence and verify integrity failure during replay.

A further test must show that changing only a future revision cannot alter a forecast reconstructed at an earlier `as_of`.

## Implementation consequence

**SERPIENTE:** expose deterministic canonical input/feature manifest construction at the forecast boundary; do not permit an arbitrary opaque fingerprint to be treated as equivalent to model-input lineage.

**CeutIA:** verify the new manifest identity when the extended contract is present; retain v1.1 compatibility only for the weaker status `PIT_ATTESTED`, never `PIT_SEMANTICALLY_VERIFIED`.

**Evaluation:** only forecasts with verified PIT semantics may enter an evaluation slice whose protocol claims exact information-set eligibility. Attested-only forecasts remain separately classified.

## Scientific state change

Previous interpretation:

`point_in_time_fingerprint present + integrity protected -> PIT integrity`

Corrected interpretation:

`point_in_time_fingerprint present + integrity protected -> PIT attestation`

`recomputed input-manifest binding -> PIT semantic verification`

## Dependencies

- canonical scientific prediction contract versioning;
- SERPIENTE point-in-time store;
- feature construction/derivation boundary;
- CeutIA cross-repository consumer;
- prospective evaluation protocol.

## Falsification condition

This handoff is invalidated if the existing producer/runtime can already prove, through executable lineage and deterministic reconstruction, that every feature supplied to `LongitudinalForecaster` is derived exclusively from the exact `PointInTimeStore.history_at(as_of)` set. Such evidence must be demonstrated by code path and test, not by field presence or documentation.
