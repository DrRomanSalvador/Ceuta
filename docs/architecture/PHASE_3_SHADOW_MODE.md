# CeutIA Phase 3 — Shadow Mode

Phase 3 establishes a production-isolated prospective evaluation path.

## Invariants

- Only observations with `available_at <= cutoff_time` may reach a shadow forecaster.
- `available_at < event_time` is a temporal leakage error.
- A shadow forecast target may not precede its cutoff.
- Shadow persistence uses a dedicated `ShadowLedger`.
- Shadow records are immutable in status: `SHADOW_EVALUATION`.
- The shadow engine exposes no production promotion or model-update operation.
- Legacy `ShadowModeExecutor` routes through the isolated engine rather than `ForecastLedger`.

## Exit criteria

The phase closes only when its verifier passes, the full CI workflow succeeds on the exact implementation commit, and the evidence is traceable to that commit SHA. Human inspection alone is insufficient.
