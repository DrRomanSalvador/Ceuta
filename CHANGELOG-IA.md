# CeutIA — AI Implementation Changelog

This file records material implementation decisions made by the primary implementation agent. It does not replace Git history and does not constitute human approval.

## 2026-09-13

- IDs: `GPT-001` through `GPT-010`
- Branch: `codex/p0-rigorous-integration`
- Change: separated epistemic status from implementation/review status and introduced point-in-time evidence eligibility.
- Change: added immutable v1 JSON Schemas for Evidence, Claim, Alert Dossier, Contradiction, Falsification Result, Review Decision, Source Provenance, Epistemic Transition, Temporal Eligibility and CeutIA-Serpiente `pull_context`.
- Change: added Pydantic enforcement for timezone-aware timestamps, publication/ingestion ordering, uncertainty, independent-source corroboration and temporal leakage prevention.
- Tests: `tests/test_p0_contracts.py` adds adversarial cases for single-source claims, dependent sources, independent corroboration, contradictions, corrections, post-event publication, future-information leakage, unknown/synthetic content, missing uncertainty and provenance.
- Status: implementation in progress; CI and human review pending.
- External red-team: none active. Grok is no longer an active worker; no Grok findings are assumed.
- Limitation: existing repository ingestion paths are not yet all wired to these new contracts.

## 2026-09-13 — Layer 1 audit

- Decision: Layer 1 classified `BLOCKED`; Layer 2 and later layers are prohibited until the observation boundary is enforced across all real consumers.
- CI evidence: `CeutIA CI` run `34750836710` succeeded; `CeutIA Security Control Plane` run `34750836633` failed in static checks after the runtime security and P0 observation suites passed.
- Direct inspection identified alternative legacy ingestion, registry, temporal and data-fetching paths that can bypass the new `EvidenceContract` / `observation_boundary.py` controls.
- Critical findings included ingestion-time-based backtest eligibility, a corroboration path capable of upgrading from a single link, optional uncertainty in the legacy evidence model, and direct legacy ingestion without observation-boundary admission.

## 2026-09-13 — Layer 1 remediation

- Legacy evidence now exposes a single `available_at` boundary with revision-aware precedence: `revision_time -> publication_time -> ingestion_time`.
- Event time is explicitly excluded from analytical availability.
- Legacy temporal filtering delegates to the canonical `available_at` boundary; callers cannot select ingestion time as an alternative analytical gate.
- Legacy ingestion validates the generated representation through `EvidenceContract` before registry/graph admission and fails closed on malformed temporal input.
- Missing quantitative uncertainty is represented explicitly as `UNKNOWN` uncertainty rather than silently omitted.
- Corroboration no longer upgrades epistemic state from a numerical independence score alone; explicit independent relationships and distinct source IDs are required.
- `contracts/v1/evidence.schema.json` now includes `revision_time`.
- Added integration/adversarial tests for revision leakage, event-time substitution, malformed timestamps, unknown epistemic state, dependent corroboration and historical backtesting.
- Current status remains `BLOCKED` pending new CI evidence and closure of the remaining `context_service` and `VerifiedData` alternative-path findings.
- No prediction layer was implemented. A mathematically complex predictor is explicitly gated on verified point-in-time integrity and out-of-sample validation.
