# CeutIA — Complex-System Interaction Formalism V1

## Objective

CeutIA must be capable of representing connected complex systems without assuming that pairwise, static, instantaneous or single-scale relationships are sufficient.

The implementation therefore adopts a formal interaction substrate capable of representing:

- multiple systems and nested subsystems;
- multiple layers/domains;
- node state and edge state;
- pairwise and higher-order interactions;
- signed amplification and damping;
- time-varying activation;
- delayed effects;
- feedback loops;
- cross-scale coupling;
- constraints and conservation/balance relations;
- interventions and exogenous disturbances;
- stochastic uncertainty;
- observational versus causal/mechanistic relation status;
- competing structural models.

## Mathematical backbone

For continuous-time state x(t) ∈ R^n, CeutIA represents the system at the level of a general dynamic equation:

`dx/dt = F_0(t,x) + Σ_e K_e(t) Φ_e(x(t-τ_e), z_e) + U(t,x,u) + ε(t)`

where:

- `F_0` is intrinsic/system-internal dynamics;
- `e` indexes interaction edges or hyperedges;
- `K_e` is the signed, potentially time-varying coupling operator;
- `Φ_e` is the interaction law;
- `τ_e ≥ 0` is an explicit delay;
- `z_e` contains scale, layer, regime and contextual metadata;
- `U` represents explicit interventions/control inputs;
- `ε` represents disturbances/noise whose semantics must remain explicit.

For discrete time:

`x_{k+1} = T_k(x_k, x_{k-d1}, …, u_k, w_k)`.

The architecture must never silently convert a discrete process into continuous dynamics or vice versa.

## Interaction order

Pairwise interaction is a special case. A higher-order interaction is represented directly as:

`Φ_{i1,…,im}(x_i1,…,x_im)` for `m > 2`.

Projecting this to pairwise edges is lossy and is therefore permitted only as an explicitly labelled analytical projection. The original hyperedge remains authoritative.

This prevents three-way or higher-order effects from being falsely represented as collections of independent pairwise effects.

## Multilayer coupling

Each node has a layer and scale. Cross-layer and cross-scale coupling is represented explicitly rather than inferred from namespace relationships.

For scales `s` and `r`, a coupling may be represented as:

`y_r = A_{r←s}(t) G_{r←s}(x_s)`.

Aggregation/disaggregation rules are part of the relation metadata. No assumption of scale invariance is permitted.

## Feedback

A directed cycle is represented as a feedback structure, not merely as an undirected correlation.

For a local linearisation around equilibrium `x*`,

`δẋ = J(x*) δx`,

where `J` is the Jacobian of the complete coupled system. Stability cannot be inferred from an individual edge. It is a property of the coupled dynamics, delays, constraints and operating regime.

For a discrete local model,

`δx_{k+1} = A δx_k`,

local asymptotic stability requires all eigenvalues of `A` to have modulus `< 1`. For continuous-time linearisation, the corresponding requirement is negative real parts of all eigenvalues of `J`.

These are model-dependent mathematical criteria, not universal empirical claims.

## Delays

Delayed interaction is represented explicitly as `x_j(t-τ)`.

A delayed edge cannot be collapsed into an instantaneous edge without recording the transformation because delay can change stability, resonance, oscillation and causal attribution.

## Constraints

The interaction network can carry structural constraints such as:

`g(x,t) = 0`

and

`h(x,t) ≤ 0`.

Constraints can encode balance, conservation, capacity, feasibility or institutional rules. A constraint is not a causal edge.

## Observational versus causal semantics

Every relation has an explicit epistemic kind. An associational edge does not become causal because it appears in a trajectory. A temporal ordering does not establish causality. A mechanistic relation requires an explicit mechanism and supporting evidence.

This distinction is enforced at the interaction-contract level.

## State, observation and intervention separation

The latent system state `x(t)`, observation process `y(t) = H_t(x(t), v(t))`, and intervention/control `u(t)` are separate objects.

Consequently:

`change in y ≠ automatically change in x`.

Changes in the measurement process `H_t` can generate apparent state changes. Changes in `u(t)` can alter subsequent observations and contaminate naive observational learning.

## Uncertainty

The architecture distinguishes:

- measurement uncertainty;
- process uncertainty;
- parameter uncertainty;
- structural/model uncertainty;
- regime uncertainty;
- scenario uncertainty;
- observability uncertainty;
- identifiability uncertainty.

Correlated uncertainties cannot be combined as independent variances without an explicit independence assumption.

## Complex-system interaction classes

The representation must permit all of the following without forcing them into one score:

1. direct pairwise coupling;
2. reciprocal coupling;
3. higher-order interaction;
4. positive feedback;
5. negative feedback;
6. delayed feedback;
7. cross-layer interaction;
8. cross-scale interaction;
9. dynamic topology;
10. time-varying coupling strength;
11. regime-conditioned coupling;
12. state-conditioned coupling;
13. exogenous forcing;
14. endogenous perturbation;
15. cascade propagation;
16. constrained flow;
17. bottleneck/queue effects;
18. competition;
19. cooperation;
20. synchronization;
21. phase-like coupling where mathematically appropriate;
22. threshold activation;
23. saturation;
24. nonlinear amplification;
25. nonlinear damping;
26. hysteresis;
27. path dependence;
28. multistability;
29. stochastic forcing;
30. measurement-induced apparent interaction;
31. selection-induced apparent interaction;
32. intervention-induced interaction;
33. adversarially induced interaction;
34. observer/model-induced feedback;
35. structural constraint interaction;
36. composition/emergence.

## Formal safeguards

CeutIA must preserve the original relation whenever an analytical projection is generated.

Pairwise projections cannot overwrite higher-order interactions.

Aggregated temporal data cannot overwrite the original resolution.

Cross-scale aggregation cannot overwrite scale-specific evidence.

Model-generated edges cannot become observational evidence.

Causal edges cannot be created solely by temporal precedence or correlation.

A feedback loop cannot be declared stable from edge-level weights alone.

A threshold cannot be treated as universal outside its estimated validity domain.

A simulation trajectory cannot become empirical evidence without independent observational support.

An intervention outcome must preserve intervention timing, fidelity, concurrent interventions and observation-process changes.

## Implementation

The formal substrate is implemented in:

`backend/app/core/complex_systems/interaction_algebra.py`

and resilience quantities in:

`backend/app/core/complex_systems/resilience_math.py`.

These are foundational mathematical contracts. They do not claim that every model family, estimator or scientific benchmark has already been implemented.

The exhaustive capability inventory remains the completeness registry. Every subsequent interaction mechanism must map to that registry and preserve this formalism rather than introduce a competing representation.
