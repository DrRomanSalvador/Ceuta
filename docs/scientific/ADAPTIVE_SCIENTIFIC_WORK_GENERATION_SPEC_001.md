# ADAPTIVE SCIENTIFIC WORK GENERATION SPECIFICATION 001

**Document ID:** `ADAPTIVE-SCIENTIFIC-WORK-GENERATION-001`
**Status:** `SPECIFIED`
**Owner:** ESPÍA (scientific semantics); INGENIERO (technical realization)
**Scope:** CeutIA + SERPIENTE + NOTARIO scientific consequence/work-generation boundary
**Date:** 2026-09-16

## 1. Purpose

Define the minimum scientific contract by which new evidence, contradictions, anomalies, validation results, model failures, observation-process changes and other material consequences may generate subsequent scientific work without creating an autonomous task-count optimizer or a recursive task loop.

This document specifies behaviour. It does not claim that the runtime implementation is complete or scientifically validated.

## 2. Canonical lifecycle

`EVIDENCE -> KNOWLEDGE UPDATE -> DISCOVERY/CONTRADICTION -> ALTERNATIVE EXPLANATIONS -> FALSIFICATION/TEST DESIGN -> RESULT -> EPISTEMIC UPDATE -> SCIENTIFIC CONSEQUENCE -> CANDIDATE WORK -> EXECUTION -> VALIDATION -> PERSISTENCE`

A negative result, contradiction, abstention or unresolved uncertainty is a valid terminal result for a candidate investigation.

## 3. Candidate-work preconditions

A candidate work item is admissible only if all required predicates are satisfied:

- material trigger exists;
- trigger has provenance;
- affected scientific object is identifiable;
- scientific question or uncertainty is explicit;
- proposed work is sufficiently defined to execute or hand off;
- work is not equivalent to an existing open/completed item unless it is a justified revision;
- objective is falsifiable or has an explicit audit/validation criterion;
- stopping condition exists;
- dependencies are represented;
- authority boundary is respected;
- expected scientific consequence is material enough to justify execution.

If these predicates are not satisfied, the system MUST preserve the unresolved state rather than synthesize a task.

## 4. Candidate record

A canonical candidate should preserve, at minimum:

- `candidate_id`
- `trigger_type`
- `evidence_ids`
- `discovery_id` or contradiction identifier where applicable
- `affected_object_ids`
- `scientific_question`
- `alternative_explanations`
- `proposed_work_type`
- `expected_information_gain_or_uncertainty_reduction`
- `decision_relevance`
- `falsification_criterion`
- `stopping_condition`
- `dependencies`
- `authority_scope`
- `provenance`
- `priority_rationale`
- `status`

A scalar scientific-value score MUST NOT be required merely to permit generation. Multi-criteria rationale is preferred because scientific value, uncertainty, feasibility, cost and risk are not generally commensurable without additional assumptions.

## 5. Anti-Goodhart constraints

The system MUST NOT optimize:

- number of tasks created;
- number of tasks closed;
- execution volume;
- agent activity;
- apparent continuity;
- number of generated hypotheses;
- number of alerts.

Task closure is evidence about workflow state, not scientific value.

A candidate should be preferred only when its scientific rationale is explicit and auditable, considering as applicable uncertainty reduction, falsification value, information gain/value of information, decision relevance, validation value, risk reduction, feasibility, cost and delay.

Hard constraints override such considerations: epistemic integrity, provenance, reproducibility, temporal/PIT validity, safety and authority.

## 6. Competing-explanation requirement

For material observations where multiple explanations are plausible, the candidate-generation layer should preserve competing hypotheses rather than selecting the most coherent explanation by default.

At minimum, when applicable:

`PHENOMENON_CHANGE`
`OBSERVATION_PROCESS_CHANGE`
`DENOMINATOR_CHANGE`
`POPULATION_COMPOSITION_CHANGE`
`OTHER_PLAUSIBLE_EXPLANATION`

The system does not infer causality merely by representing alternatives. It generates discriminating tests where scientifically justified.

## 7. Falsification lifecycle

A material discovery should be transformable into:

`DISCOVERY -> HYPOTHESIS -> ALTERNATIVE -> DIFFERENTIAL PREDICTION -> FALSIFICATION TEST -> RESULT -> UPDATE`

Allowed outcomes include:

- `SUPPORTED_WITHIN_SCOPE`
- `CONTRADICTED`
- `REVISED`
- `ABSTAINED_INSUFFICIENT_EVIDENCE`
- `INCONCLUSIVE`
- `NOT_EXECUTABLE`

`NOT_EXECUTABLE` is not equivalent to scientific support.

## 8. Duplication and recursion control

Before creating candidate work, the system must compare against existing work using semantic identity, affected objects, trigger/evidence provenance and scientific question. Exact textual similarity is insufficient.

A candidate generated from its own immediate closure must not recursively regenerate itself without a new material trigger.

An audit whose only consequence is another equivalent audit is not material work.

## 9. Value of information boundary

Where a decision or scientific uncertainty makes information acquisition relevant, VOI/EVSI-style reasoning may inform prioritization. It MUST NOT be represented as an exact numerical truth when utility, probabilities, costs or counterfactual decision effects are not identified.

A candidate may therefore carry a qualitative or bounded rationale such as:

- high uncertainty reduction / low acquisition cost;
- high falsification value;
- high decision relevance / unresolved evidence;
- validation prerequisite;
- low value because it cannot discriminate among plausible explanations.

## 10. Temporal and intervention integrity

Candidate work involving prediction/evaluation MUST preserve point-in-time boundaries. Future-derived information cannot be used to justify an origin-time investigation.

Candidate work involving interventions MUST distinguish:

`FORECAST -> DECISION -> INTERVENTION -> EXPOSURE -> OBSERVED OUTCOME`

The resulting outcome cannot be interpreted as an untreated forecast outcome without an appropriate design.

## 11. Capability boundary

Implementation of this specification does not establish:

- scientific truth authority;
- autonomous causal inference;
- prospective predictive validity;
- intervention effectiveness;
- operational early-warning effectiveness;
- catastrophe prediction;
- correct real-world Ceuta denominators;
- correct real-world observation-process measurement.

Those claims require their own evidence and validation states.

## 12. Minimum adversarial suite for technical realization

The eventual implementation must test at least:

1. duplicate candidate from identical evidence;
2. duplicate candidate under changed wording;
3. recursive self-generation after closure without a new trigger;
4. task generated from non-material evidence;
5. task without provenance;
6. task without stopping condition;
7. task exceeding authority scope;
8. task based on future-derived evidence;
9. confirmation-only pathway with no alternative explanation where alternatives are scientifically required;
10. observation-process drift misclassified as phenomenon deterioration;
11. denominator drift misclassified as phenomenon deterioration;
12. contradiction incorrectly converted into confirmation;
13. failed test incorrectly converted into support;
14. intervention-contaminated outcome treated as ordinary prospective outcome;
15. task-count optimization creating scientifically empty work.

## 13. Closure states

`DISCOVERED -> ANALYZED -> SPECIFIED -> HANDOFF_READY -> IMPLEMENTED -> TESTED -> VERIFIED -> VALIDATED -> ESTABLISHED`

A candidate is not closed merely because it has been generated or handed off. Scientific closure requires the evidence appropriate to its specific claim.

## 14. Traceability

Every material candidate must preserve:

`DISCOVERED_BY`
`PROPOSED_BY`
`IMPLEMENTED_BY`
`REVIEWED_BY`
`VALIDATED_BY`
`AUTHORIZED_BY`

only where the corresponding action actually occurred. Unknown attribution MUST remain unknown.

## 15. Fixed-point condition

Adaptive work generation reaches a scientific fixed point only when no candidate remains that is simultaneously material, justified, non-duplicative, sufficiently specified, executable within authority, and capable of producing additional validated scientific progress under the current evidence boundary.

External evidence requirements, unavailable infrastructure and human-only authority decisions remain explicit boundary states; they do not justify fabricated completion.
