# CeutIA Unified System Kernel V1

## Purpose

CeutIA now has a domain-neutral kernel for representing an evolving complex system as one auditable object rather than as independent analytical modules.

The canonical lifecycle is:

`Observation → State → Trajectory → Dynamics → Uncertainty → Relations → Hypotheses → Causality → Prediction → Decision → Response → Learning → new State`

The kernel does not replace specialist mathematics. It provides the common representation and execution boundary through which specialist methods become composable.

## Canonical object

`SystemContext` remains the canonical state/evidence context. `ClosedLoopSnapshot` is the temporal execution record for one inference cycle, and `SystemKernel` is the append-only memory of those cycles.

Each cycle preserves:

- system identity and event time;
- observations and evidence lineage;
- current state and complete trajectory;
- transition/dynamic records;
- uncertainty and model references;
- relations and competing hypotheses;
- causal-model references without assuming causal validity;
- predictions;
- decision context and recommendation;
- intervention/response records;
- learning records;
- complete cross-stage lineage;
- explicit epistemic level at every stage.

## Scientific separation

The kernel enforces semantic separation rather than collapsing everything into one score:

`observation != estimate != association != hypothesis != causal explanation != forecast != recommendation != intervention != observed response != learned causal effect`

A causal stage is labelled causal only when a causal-model reference is explicitly supplied. A prediction remains predictive. A recommendation remains conditional on its supplied scenarios, uncertainty and assumptions.

## Real-time operation

`ClosedLoopEngine.process()` performs bounded orchestration at event arrival. `process_into()` appends the resulting snapshot to `SystemKernel` while enforcing strictly increasing cycle time.

This is an architectural real-time boundary, not a claim that every specialist method is computationally real-time. Computationally expensive methods can execute asynchronously while the kernel preserves the same lineage and epistemic chain.

## Mathematical architecture

The kernel is compatible with a layered probabilistic representation:

`P(x_t, z_t, M_t, H_t | Y_0:t, A_0:t, C_t)`

where `x_t` is latent/system state, `z_t` dynamic/regime structure, `M_t` model structure, `H_t` competing hypotheses, `Y` observations, `A` interventions/actions, and `C` contextual/structural constraints.

No single probability expression is treated as a universal model. Each specialist engine must declare its assumptions, estimand, observation process, uncertainty structure, validity domain and failure conditions.

## Reuse across domains

The kernel contains no health-specific ontology. The same representation can model health systems, ecosystems, infrastructure, organizations, economies, security environments, climate-linked systems, or coupled multi-domain systems.

Domain knowledge enters through observations, variables, relations, hypotheses, causal models, constraints and specialist estimators.

## Decision loop

Decision is downstream of state, dynamics, uncertainty and predictive/scenario information. When inference is not decision-ready, the engine fails closed through abstention rather than generating a confident recommendation.

The existing decision layer remains responsible for utility, robust, regret and harm-minimization policies. Value of information and richer intervention-effect estimation remain specialist extensions to be connected through the same kernel contract.

## Learning loop

Response and learning are represented as explicit records rather than being inferred from the mere existence of a decision. This permits prospective outcome evaluation, failed-hypothesis memory, model updating and champion/challenger mechanisms to be attached without contaminating the original evidence lineage.

## What this closes

This architecture closes the structural gap between the previously implemented trajectory, state-estimation, dynamics, uncertainty, interaction, causal, forecasting and decision components: they now have one reusable lifecycle and one temporal memory boundary.

It does **not** claim that every specialist scientific method is complete. Remaining work belongs inside the kernel's extension points: full multivariate/nonlinear Bayesian estimation, switching and hierarchical state-space inference, rigorous causal identification/estimation, calibrated probabilistic forecasting, synchronized simulation, intervention-effect estimation, online learning, privacy enforcement and prospective scientific validation.

Final CI and scientific validation remain intentionally deferred until the implementation cycle is complete.
