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
- Critical findings include ingestion-time-based backtest eligibility, a corroboration path capable of upgrading from a single link, optional uncertainty in the legacy evidence model, and direct legacy ingestion without observation-boundary admission.
- Documentation updated in `CURRENT_STATUS.md` with the exact blockers and prohibited next actions.
