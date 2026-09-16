# Mission Evolution Engine

**Status:** ACTIVE control-plane capability

The Mission Evolution Engine is the permanent admission and lifecycle mechanism for deciding whether a new mission is justified. It is not itself a mission and does not replace the common registry or the deployment orchestrator.

## Operational loop

`ACTION_X → CAPABILITY AUDIT → EXTENSION TEST → COLLABORATION TEST → TEMPORARY TASK-FORCE TEST → SIX-GATE ADMISSION → AUTHORIZATION → CONTRACT GENERATION → PROMPT GENERATION → REGISTRATION → ZERO-CONTEXT VALIDATION → OBSERVATION → REVIEW → RETIRE/REVISE`

## Mandatory precedence

1. Existing capability
2. Existing mission extension
3. Cross-mission collaboration
4. Temporary task force
5. New permanent mission

The engine fails closed at the first viable earlier solution. A mission is not admitted merely because it can perform a task.

## Six mandatory gates

A permanent mission reaches `ADMIT` only when all are satisfied:

- **NECESSITY:** a concrete ACTION_X is required by the system.
- **NON_REDUNDANCY:** existing mandates cannot perform it adequately and cooperation does not solve it.
- **MARGINAL_VALUE:** net system value is positive after complexity, coordination, failure, maintenance, duplication and security costs.
- **COHERENCE:** the proposed scope forms a stable architectural identity.
- **INTEGRABILITY:** the mission can use the common control-plane contract, authority and state model.
- **VALIDATABILITY:** the contribution has an explicit validation plan.

Evidence must be explicit and traceable. Missing evidence blocks admission; it is never converted into certainty.

## Centrality and marginal value

Centrality is recorded against downstream dependencies, enabled tasks, scientific importance, risk reduction, validation importance, cross-mission relevance, required-use frequency, irreversibility if missing and decision impact.

Marginal value is evaluated as system delta rather than agent capability. The engine records positive and negative dimensions separately so complexity cannot disappear inside an aggregate score.

## Admission versus authorization

`MissionEvolutionEngine.decide()` determines whether the architecture has reached an admission decision. `MissionEvolutionEngine.authorize()` separately requires `CAN_AUTHORIZE`. This prevents a proposing agent from creating its own authority.

The engine generates a machine-readable contract and a provider-neutral canonical prompt only from an admitted proposal. The generated prompt is not proof of existence; the canonical registry remains the discovery source.

## Zero-context requirement

A generated mission is not operationally integrated until a context-free agent can discover its identity, purpose, contract, state, invocation method, current task, authority and limitations through the persisted control-plane artifacts and execute it through the host/orchestrator.

## Concurrency and persistence boundary

Admission proposals and registry changes must be versioned and reconciled. A stale writer must fail closed. The repository implementation intentionally does not fake live distributed leases or transactions; those remain a deployment-orchestrator responsibility.

## Retirement

Lifecycle review must compare observed value against complexity and maintenance cost. A mission can be proposed for retirement or revision when it becomes redundant, inactive, persistently unvalidated, excessively costly, or no longer coherent with the control plane.
