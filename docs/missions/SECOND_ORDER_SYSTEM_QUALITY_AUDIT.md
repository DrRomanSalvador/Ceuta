# MISSION 13 — NOTARIO
# SECOND-ORDER SYSTEM QUALITY AUDIT

**Scope:** collective intelligence, discovery, scientific learning, systemic quality, and emergent capability above constitutional compliance.

**Audit basis:** repository `main` at `47bdd7db9089884a28ced56fd04e6b7f7be18233`, plus Mission 13 constitutional branch `mission-13-notario-constitution` at `8b85b048c01390f8674604802d94fdc14c503265`.

**Important boundary:** this document does not redefine the permanent constitution and does not create a second governance layer. It records second-order capability status and actionable gaps.

## 1. Executive finding

CeutIA already contains an unusually broad set of primitives for second-order scientific intelligence: rival hypotheses, falsification, source-independence modelling, evidence dependence graphs, value-of-information computation, calibration/scoring, longitudinal temporal machinery, closed-loop prediction→decision→response→learning structures, model disagreement, domain coupling, blind-spot artefacts, and a sparse mission collaboration graph.

The principal remaining problem is **not absence of components**. It is the missing transversal composition layer that turns those components into a measurable organizational learning system.

The most material gaps are:

1. **Spontaneous discovery intake is not yet a first-class transversal capability.** The repository contains anomaly/weak-signal/hypothesis machinery, but no demonstrated organization-wide discovery funnel that turns unexpected observations into durable candidate discoveries and then routes them through falsification.
2. **Disagreement exists as evidence/model conflict, but there is no demonstrated cross-mission disagreement lifecycle with explicit disagreement type, resolution experiment, minority preservation, and unresolved-state telemetry.**
3. **Scientific knowledge dependency and blast-radius infrastructure is incomplete at the organization level.** Source dependence exists, and decision lineage exists, but a demonstrated SOURCE→CLAIM→MODEL→RESULT→DECISION→DOWNSTREAM-CLAIM impact graph is not established as one transversal graph.
4. **Scientific debt is not yet a first-class portfolio.** Technical/validation artifacts exist, but there is no demonstrated debt ledger with exposure, owner, ageing, consequence, and repayment strategy separated from technical debt.
5. **Capability regression and longitudinal collective-intelligence benchmarks are not yet demonstrated as a coherent evaluation system.** Tests are numerous; organizational capability measurement is different from test volume.
6. **Reality anchoring and outcome learning exist in components, but prospective operational linkage is not yet demonstrated as a transversal organizational loop.**
7. **Metric anti-Goodhart analysis is not yet a systematic governance process over the whole metric inventory.**
8. **Emergent capability detection is conceptually represented by interaction/complex-system components but is not yet an explicit registry and validation workflow.**
9. **Knowledge obsolescence/freshness is represented in temporal and drift components but lacks a transversal claim-level reevaluation policy and portfolio.
10. **Research portfolio allocation is partially represented through decision/VoI primitives but not yet as a system-level scheduler whose objective is collective information gain rather than local task completion.**

These gaps should not automatically become new missions. Most can be addressed by extending existing evidence, knowledge, decision, learning, metrics, and orchestration surfaces.

## 2. Existing second-order capabilities

### 2.1 Hypothesis generation and rival explanations — EXISTING / PARTIAL TRANSVERSALITY

`backend/app/core/epistemology_p0/advanced/hypotheses.py` defines falsifiable hypotheses with predictions, favourable and contrary evidence, confounders, missing data, verification cost, action/inaction consequences, and an explicit falsification criterion. It also provides a rival-hypothesis set rather than a single-explanation model. This is a strong foundation for anti-confirmation-bias reasoning.

Gap: the primitive is scientific and claim-oriented, not yet demonstrated as a system-wide spontaneous-discovery intake and routing mechanism.

### 2.2 Active falsification — EXISTING

The repository contains dedicated falsification components and falsification-result contracts, plus adversarial validation. The hypothesis model explicitly requires a falsification criterion.

Gap: no demonstrated universal policy saying when material hypotheses must trigger disconfirmatory search rather than merely allowing it.

### 2.3 Source independence — EXISTING

`epistemology_p0/sources/independence.py` explicitly models shared communiqués, textual copying, citation chains, shared interests, same methods, and unknown dependence. `evidence/dependence_graph.py` independently models dependency and common origin. This directly prevents simple source counting from being mistaken for independent evidence.

Gap: there are two related source-dependence surfaces. They are not yet demonstrated as one canonical organization-wide independence service.

### 2.4 Value of information — EXISTING / DECISION-LOCAL

`decision/value_of_information.py` computes expected value with and without information and subtracts acquisition cost. It therefore correctly makes information value decision-dependent rather than treating information as intrinsically valuable.

Gap: no demonstrated organization-level research portfolio allocator that uses VoI plus uncertainty, impact, dependency centrality and cognitive cost across missions.

### 2.5 Closed-loop learning — EXISTING / STRONG PRIMITIVE

`system/closed_loop.py` represents observation, state, trajectory, dynamics, uncertainty, relations, hypotheses, causality, prediction, decision, response and learning. The kernel persists temporal snapshots and lineage.

Gap: `closed_loop_complete` is a structural property (`response_ids` and `learning_ids`) rather than proof that real-world outcomes have been observed and attributed. Organizational outcome learning remains an evidence problem, not merely a field-presence problem.

### 2.6 Decision/prediction distinction — EXISTING

Decision, prediction, uncertainty, information requests, outcome records, and decision lineage are represented separately. This supports the required distinction between model performance and decision value.

Gap: a longitudinal benchmark linking prediction quality → decision quality → real-world outcome quality is not demonstrated as one organization-wide evaluation surface.

### 2.7 Temporal learning and drift — EXISTING / PARTIAL

The repository contains temporal alignment, point-in-time eligibility, change-point, regime detection, longitudinal validation, calibration drift, temporal feedback, and temporal model components.

Gap: claim-level freshness and obsolescence management is not demonstrated as a single transversal service with reevaluation triggers and downstream impact propagation.

### 2.8 Calibration and uncertainty — EXISTING

Forecasting calibration, scoring, uncertainty flow, epistemic validation, model disagreement, and abstention are represented in code and tests.

Gap: confidence decomposition across data/measurement/interpretation/model/forecast/causal applicability is not demonstrated as a common contract for all material claims.

### 2.9 Systemic interaction modelling — EXISTING / PARTIAL

The repository contains complex-system interaction algebra, dynamic networks, coupling, propagation, cascade-risk and system-intelligence components. The closed-loop model explicitly includes cross-stage dependencies.

Gap: these are mainly domain/system primitives. There is no demonstrated organizational-level systemic-failure catalogue connecting mission interfaces, shared assumptions, correlated blind spots and cross-mission failure incidents.

### 2.10 Collaboration architecture — EXISTING

`MISSION_COLLABORATION_GRAPH.md` defines scientific information flows, required artifacts, conflict handling, separated validation, and sparse-edge discipline. It explicitly states that new edges require recurring scientific need, differentiated method and measurable reduction in blind spots.

Gap: collaboration topology is prescribed, but there is no demonstrated longitudinal measurement of whether collaboration actually increases information gain or discovery relative to isolated work.

## 3. Partial capabilities requiring composition

| Capability | Status | Evidence | Principal gap |
|---|---|---|---|
| Spontaneous discovery | PARTIAL | hypotheses, weak signals, anomaly/detection components | no canonical discovery funnel |
| Hypothesis generation | EXISTING | rival hypothesis model | not organization-wide intake |
| Falsification | EXISTING | falsification modules/contracts/tests | no universal materiality trigger |
| Alternative explanations | EXISTING | H1-H5 rival set | no longitudinal alternative-survival analytics |
| Cognitive diversity | PARTIAL | model alternatives/disagreement, collaboration graph | diversity dimensions not jointly measured |
| Independence | EXISTING | source independence + dependence graph | duplicate canonical surfaces |
| Productive dissent | PARTIAL | conflict resolution + model disagreement | no disagreement lifecycle |
| Information value | EXISTING | VoI engine | not portfolio-wide |
| Resource allocation | PARTIAL | resource optimizer + decision optimization | no collective research scheduler |
| Stopping rules | PARTIAL | decision/review/closure mechanisms | no general scientific stopping contract |
| Anti-Goodhart | PARTIAL | metrics integrity/tests/policy | no systematic metric threat model |
| Failure learning | PARTIAL | incident/audit/adversarial machinery | weak generalization-to-rule loop |
| Scientific regression | PARTIAL | longitudinal validation + lineage | no claim-level invalidation propagation |
| Dependency impact | PARTIAL | source dependence + decision lineage | no canonical knowledge graph |
| Blast radius | MISSING | scattered lineage/dependency primitives | no unified impact traversal |
| Scientific debt | MISSING | risks/open questions/validation gaps | no dedicated debt portfolio |
| Technical/scientific debt separation | PARTIAL | separate engineering/scientific artifacts | no shared debt taxonomy |
| Freshness/obsolescence | PARTIAL | drift/change-point/temporal components | no claim-level reevaluation service |
| Reality anchor | PARTIAL | observations, outcomes, interventions | no universal claim-to-world validation status |
| Outcome loop | EXISTING / PARTIAL | closed loop + outcome records | no demonstrated prospective organizational learning |
| Counterfactual learning | EXISTING / DOMAIN-SPECIFIC | counterfactual engine + causal modules | applicability varies by domain |
| Ensemble intelligence | PARTIAL | multimodel forecasting/model disagreement | no general ensemble value test |
| Redundancy | PARTIAL | deduplication + independence | no marginal redundancy policy |
| Meta-evaluation | PARTIAL | validation/adversarial systems | no explicit validation-of-validation registry |
| Benchmarks | PARTIAL | extensive tests/validation suites | no longitudinal capability benchmark |
| Capability regression | MISSING | CI/regression tests | no explicit capability inventory comparison |
| Emergent capability | MISSING | complex-system interaction primitives | no emergent-capability registry |
| Complexity budget | PARTIAL | architecture/gap audits | no marginal-capability vs complexity ledger |
| Documentation fidelity | PARTIAL | docs + code + CI | no automated docs↔implementation coverage audit |
| Observer observability | EXISTING / PARTIAL | observability/self-monitoring | no collective-intelligence dashboard |
| Minimum sufficient record | PARTIAL | provenance/audit records | no cross-system sufficiency standard |
| Domain translation | PARTIAL | domain coupling/semantic contracts | no translation-loss assessment |
| Ontology drift | EXISTING / PARTIAL | ontology + semantic identity + schema drift | no formal ontology revision impact process |
| Epistemic calibration | EXISTING | calibration/scoring/abstention | transversal claim-level calibration incomplete |
| Blind-spot discovery | EXISTING / PARTIAL | blind-spot capability map/resolution | no continuous system-wide blind-spot discovery loop |
| Negative space | PARTIAL | observation boundaries/missingness | no universal `CANNOT_OBSERVE` registry |
| Unknown unknowns | PARTIAL | anomalies, weak signals, observer effect | no dedicated detection/evidence lifecycle |
| Research portfolio | PARTIAL | VoI, optimization, mission priorities | no exploration/exploitation portfolio policy |
| Scientific long memory | PARTIAL | provenance, failed tests, adversarial records | no explicit reusable failed-hypothesis knowledge base |
| Cross-mission transfer | EXISTING / PARTIAL | collaboration graph + contracts | transfer effectiveness not measured |
| Temporal learning | EXISTING / PARTIAL | longitudinal machinery | organizational claim freshness incomplete |
| System self-audit | PARTIAL | adversarial/metrics/audit components | no periodic second-order audit executor |

## 4. Missing or material transversal capabilities

### 4.1 Discovery Funnel — MISSING

Required conceptual chain:

`OBSERVATION / ANOMALY / DISCREPANCY / WEAK SIGNAL`
→ `DISCOVERY CANDIDATE`
→ `QUESTION`
→ `HYPOTHESES`
→ `DISCONFIRMATORY TEST`
→ `EVIDENCE`
→ `SCIENTIFIC STATUS`
→ `TRANSFER / REJECTION / KNOWLEDGE`

This should not replace the existing hypothesis engine. It should be a thin transversal intake and provenance layer around it.

### 4.2 Disagreement Lifecycle — MISSING

Required fields should distinguish:

- evidence disagreement;
- assumption disagreement;
- definition disagreement;
- temporal-scope disagreement;
- methodological disagreement;
- model disagreement;
- interpretation disagreement;
- incomplete-information disagreement.

Each material disagreement should retain both sides, shared premises, discriminative evidence required, unresolved status, and minority preservation. Consensus must never be used as truth evidence by itself.

### 4.3 Knowledge Impact Graph — MISSING

A canonical graph should support:

`SOURCE → CLAIM → ASSUMPTION → METHOD/MODEL → RESULT → DECISION → OUTCOME → DOWNSTREAM CLAIM`

and reverse traversal:

`changed node → affected descendants → required revalidation`.

This is distinct from mission lineage and source dependence. It is the organizational scientific-dependency graph.

### 4.4 Scientific Debt Portfolio — MISSING

Required separation:

`TECHNICAL_DEBT`
vs
`SCIENTIFIC_DEBT`
vs
`EPISTEMIC_DEBT`.

Each debt item should record consequence, evidence gap, affected claims/capabilities, owner, ageing, priority rationale, and repayment/revalidation strategy.

### 4.5 Capability Regression Benchmark — MISSING

A release should be able to answer:

`WHAT DID WE GAIN?`
`WHAT DID WE LOSE?`
`WHAT CHANGED?`
`WHAT BECAME MORE FRAGILE?`

This requires capability-level benchmark definitions, not more unit tests.

### 4.6 Emergent Capability Registry — MISSING

The system should record capabilities that arise from interaction between components without prematurely assigning them to one mission. Minimum evidence should include source interactions, observation, reproducibility/validation status, affected capabilities, and coordinator/owner only after justified assignment.

### 4.7 Metric Threat Model — MISSING

For every important metric, record intended construct, proxy failure mode, gaming strategy, reward-hacking path, counter-metric, and whether optimization could damage an unmeasured property.

### 4.8 Research Portfolio / Exploration–Exploitation — PARTIAL

VoI exists and is decision-aware, but it is not yet an organization-level allocator. A future implementation should avoid a single opaque score. Portfolio decisions should remain decomposable into information gain, decision relevance, uncertainty reduction, cost, time, risk, dependency centrality, and exploration value.

## 5. Redundancy / architecture hazards

### 5.1 Source independence duplication

There are two materially overlapping implementations: `epistemology_p0/sources/independence.py` and `evidence/dependence_graph.py`. They have different semantics and granularity. This is not automatically wrong, but a future canonicalization decision is required to avoid divergent definitions of “independent evidence.”

Classification: **REDUNDANT / REQUIRES_RESEARCH**.

### 5.2 Lineage fragmentation

Decision lineage, source dependence, provenance, scientific traceability and mission collaboration artifacts exist, but no evidence establishes that they compose into one traversable knowledge-impact graph.

Classification: **PARTIAL / MATERIAL**.

### 5.3 Metric surface area

The repository contains a very large metric surface and a duplicate-inventory skeleton. This creates a Goodhart and complexity risk even where individual metrics are correct. The next step should be metric governance, not additional metrics.

Classification: **PARTIAL / MATERIAL**.

## 6. What should NOT be implemented now

The following should be rejected as unnecessary complexity unless evidence later demonstrates material value:

1. A single global “collective intelligence score.”
2. A single universal agent-quality score.
3. A fixed number of agents per investigation.
4. A universal confidence number replacing decomposed uncertainty.
5. Automatic consensus-to-truth promotion.
6. Automatic mission creation for every newly detected capability.
7. Automatic expiration dates on all knowledge.
8. A mandatory ensemble for every prediction.
9. A universal VoI formula that ignores decision context.
10. A new orchestration hierarchy solely to manage second-order quality.
11. More documents whose only function is to restate existing constitutional rules.
12. More tests that do not measure a distinct property.

Classification: **REJECTED_AS_NON_VALUE_ADDING** pending contrary evidence.

## 7. Research-required questions

1. What measurable definition of “collective intelligence gain” can distinguish collaboration from simple parallelism?
2. How should marginal information gain be estimated when investigations share data, models or assumptions?
3. What is the least complex useful disagreement lifecycle?
4. What evidence is sufficient to declare a capability genuinely emergent rather than merely a composition of existing capabilities?
5. How should scientific debt be priced without converting uncertainty into an arbitrary score?
6. Which capability benchmarks predict real-world scientific utility rather than benchmark gaming?
7. How should discovery exploration be balanced against closure of high-value existing work?
8. What evidence establishes that cross-mission transfer materially improves results?

Classification: **REQUIRES_RESEARCH**.

## 8. Engineering handoffs required

### H1 — Knowledge Impact Graph

**Owner candidate:** INGENIERO / existing provenance-lineage owners.

**Need:** canonical graph traversal from changed source/claim/model/result to downstream objects requiring revalidation.

**Must integrate:** existing source dependence, evidence provenance, decision lineage and scientific traceability; no parallel lineage system.

**Acceptance:** a synthetic mutation of a canonical upstream node identifies exactly the affected downstream nodes and produces proportional revalidation obligations.

### H2 — Discovery Funnel

**Owner candidate:** existing epistemology/scientific runtime owners.

**Need:** persistent discovery-candidate intake connected to existing hypothesis/falsification machinery.

**Acceptance:** an unexpected anomaly can be persisted, routed into rival hypotheses, subjected to falsification, and remain explicitly unvalidated until evidence supports promotion.

### H3 — Disagreement Lifecycle

**Owner candidate:** governance/evidence owners.

**Need:** typed disagreement object with minority preservation and discriminative-test state.

**Acceptance:** unresolved disagreement survives serialization, cannot be silently collapsed into consensus, and can generate a discriminative investigation.

### H4 — Capability Regression Benchmark

**Owner candidate:** QA/engineering + architecture.

**Need:** capability-level longitudinal benchmark independent of raw test count.

**Acceptance:** a simulated release can demonstrate gain/loss/change/fragility across a stable benchmark corpus.

### H5 — Scientific Debt Ledger

**Owner candidate:** NOTARIO + engineering integration.

**Need:** separate scientific/epistemic debt portfolio linked to affected claims and validations.

**Acceptance:** a known unvalidated material claim creates a debt item whose resolution changes the affected knowledge state without confusing it with technical debt.

## 9. Priority assessment

### P0 — material collective-intelligence infrastructure

- Knowledge Impact Graph.
- Discovery Funnel.
- Disagreement Lifecycle.

Reason: these three capabilities directly determine whether independent rigorous work becomes cumulative intelligence rather than disconnected outputs.

### P1 — systemic learning and quality

- Capability Regression Benchmark.
- Scientific/Epistemic Debt Ledger.
- Metric Threat Model.
- Claim freshness/obsolescence propagation.
- Cross-mission transfer effectiveness.

### P2 — research before implementation

- Formal collective-intelligence gain metric.
- Emergent capability measurement theory.
- Exploration/exploitation portfolio optimization.
- Complexity budget formalization.
- Universal negative-space/unknown-unknown indicators.

## 10. Mission admission conclusion

No new mission is justified by this audit at present.

The principal gaps map naturally onto existing epistemology, evidence, provenance, governance, QA, learning, metrics and engineering responsibilities. Mission Evolution Engine should only be invoked later if a concrete implementation gap remains after those existing owners have attempted extension and the admission criteria are met.

## 11. Final system-quality conclusion

The repository is beyond the stage of merely having “good rules.” It already contains many ingredients of a collective scientific architecture.

The next architectural threshold is **composition**:

`DISCOVERY`
`+ DISAGREEMENT`
`+ INDEPENDENCE`
`+ FALSIFICATION`
`+ INFORMATION VALUE`
`+ DEPENDENCY GRAPH`
`+ OUTCOME LEARNING`
`+ CAPABILITY REGRESSION`
`→ `COLLECTIVE INTELLIGENCE`

The critical distinction is:

**The repository currently has many strong scientific components. It does not yet demonstrate that the organization itself learns, discovers, reallocates cognitive resources, and accumulates cross-mission intelligence as a first-class measurable phenomenon.**

That is the second-order frontier.
