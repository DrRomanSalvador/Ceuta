# CeutIA — Semantic Contract

**Document class:** Normative engineering contract
**Scope:** metrics, analytical transformations, evidence transformations, and interfaces between epistemic layers.

## Purpose

A numerical result is not sufficient to establish semantic equivalence. A refactor is interchangeable only when its mathematical behaviour and its semantic contract remain compatible.

Every important metric or transformation must therefore define:

- formula or algorithm;
- input domain and shape;
- output domain and range;
- units;
- normalization convention;
- missing-data policy;
- NaN policy;
- zero/division policy;
- error/precondition policy;
- temporal semantics;
- spatial semantics;
- epistemic role;
- dependencies;
- version.

## Reconstruction rule

When duplicate implementations are discovered, textual similarity is only a discovery signal. Classification must be based on semantic behaviour.

Use these classifications:

- `IDÉNTICA`: same implementation semantics.
- `EQUIVALENTE`: same semantics with cosmetic/refactoring differences.
- `PARCIAL`: same conceptual operation but a meaningful domain, normalization, boundary, or error-policy difference exists.
- `DISTINTA`: materially different mathematical or algorithmic semantics.
- `INCOMPATIBLE`: the implementations cannot safely serve the same contract.

The discriminant question is:

> Is there a valid input for which the implementations differ in a semantically relevant way?

If yes, they must not be silently fused.

## Required regression strategy

For every reconstructed implementation:

1. Test ordinary valid inputs.
2. Test the boundary of the declared domain.
3. Test zero denominators and empty inputs where applicable.
4. Test NaN and missing values according to the declared policy.
5. Test normalization conventions explicitly, including `N` versus `N-1` where relevant.
6. Test unit and shape constraints.
7. For `PARCIAL`, `DISTINTA`, or `INCOMPATIBLE` candidates, include a discriminating input that demonstrates the difference.
8. Preserve a regression test for every retained semantic variant before replacing a legacy implementation.

## Epistemic safety

A semantic contract must declare the epistemic role of its output. In particular:

- evidence confidence must not silently become event probability;
- association must not silently become causation;
- missing information must not silently become zero;
- dependent sources must not silently become independent evidence;
- a proxy or descriptive metric must not silently become an operational risk score.

These rules extend the existing evidence and epistemic contracts; they do not replace them.

## Implementation

The executable contract model is `app.core.semantic_contract.SemanticContract`.
It is intentionally independent of numerical libraries so that semantic compatibility can be checked without coupling the contract layer to a specific implementation.
