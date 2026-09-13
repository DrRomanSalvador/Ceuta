# ADR-0001 — Decision inicial de gobernanza documental

- Date: 2026-09-13
- Status: ACCEPTED
- Decision owner: sole human owner (drsalvadorroman-beep) via authorised agent action

### Context

The repository contained substantial documentation and a partial implementation (Cycle 1) but lacked a single verifiable status document, a closed epistemic vocabulary, and explicit contracts for evidence and the proxy-gate.

### Decision

Adopt the minimal rigorous structure under `docs/`, `docs/spec/`, `contracts/`, `work/` and related paths, with CURRENT_STATUS.md as the single source of engineering truth and the closed epistemic-state vocabulary as binding.

### Consequences

- Agents must consult CURRENT_STATUS.md before claiming any implementation status.
- Historical claims that contradict live code are to be treated as HISTORICAL.
- Further structural work on metrics.py is deferred until validation evidence exists.
