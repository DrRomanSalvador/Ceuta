# Dynamic Trajectory Engine

CeutIA now exposes domain-agnostic primitives for describing state change rather than treating each snapshot independently.

The first increment provides:

- first temporal derivatives between adjacent states;
- explicit displacement after a perturbation;
- recovery fraction relative to a baseline;
- recovery time.

These are descriptive dynamic metrics. They do not establish the cause of a transition, predict a future state, detect a regime change, or define a system as resilient/non-resilient without domain-specific criteria.

A recovery episode is represented as baseline -> perturbation -> recovery. A recovery fraction above or below a chosen threshold must not be interpreted without a domain-specific scale and decision policy.

The engine deliberately consumes the canonical trajectory substrate so dynamic analysis remains traceable to time-indexed states.

Future work includes vector-valued reserve/capacity, regime-conditioned dynamics, nonlinear response, hysteresis, critical slowing-down indicators, multistability, cross-scale coupling, and uncertainty propagation. Those capabilities require explicit mathematical definitions and synthetic benchmarks before validation.
