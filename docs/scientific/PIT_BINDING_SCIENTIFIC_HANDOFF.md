# P0 Scientific Handoff — Point-in-Time Information-Set Binding

Mission: `CROSSREPO-ENDPOINT-001`

Current v1.1 cross-repository evidence proves presence, persistence and integrity protection of `point_in_time_fingerprint`, and replay enforces stored `origin_time`/`available_at`. It does not prove that the fingerprint equals the exact information set used by SERPIENTE's model.

SERPIENTE `PointInTimeStore.fingerprint(as_of)` hashes visible observation history, while `LongitudinalForecaster.forecast(...)` accepts that fingerprint separately from feature matrix `X`. No executable lineage currently proves `X = phi(H_t)` where `H_t` is the exact visible observation set at forecast origin.

Scientific interpretation: current state is `PIT_ATTESTED`, not `PIT_SEMANTICALLY_VERIFIED`.

Required minimum extension before claiming semantic PIT integrity:
- `information_set_as_of`
- canonical `observation_manifest_hash`
- canonical `feature_manifest_hash`
- derivation method/version
- derivation configuration hash
- source/revision visibility rule
- feature availability cutoff
- reconstructible input lineage

Failure conditions: future feature timestamp, unavailable source/revision, missing derivation identity, manifest mismatch, unknown transformation lineage, or inability to reconstruct eligibility.

Falsification tests:
1. Compare a forecast using only observations visible at `t` against one injecting a post-`t` observation; the latter must be distinguishable and rejected.
2. Mutate the input manifest after persistence; replay must fail integrity.
3. Add a future revision and verify an earlier `as_of` replay is unchanged.

Do not overload v1.1 fields. If semantic binding cannot be represented without ambiguity, use a versioned contract extension and keep v1.1 at `PIT_ATTESTED`.

This requirement is an identifiability correction, not a documentation preference.
