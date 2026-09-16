# Mission Coverage Matrix — CeutIA + SERPIENTE

Legend: **D** discovers/questions, **A** analyzes, **I** implements (technical ownership), **V** verifies/validates, **C** challenges/contradicts, **P** persists/maintains epistemic state. `—` means no primary responsibility.

## Domain × mission

| Domain / capability | 01 ENG | 02 ESPÍA | 03 LIB | 04 GROK | 05 FORJA | 06 CRONOS | 07 ATLAS | 08 NEXO | 09 ORÁCULO | 10 CENTINELA | 11 MÉDICO | 12 ESTRATEGA | 13 NOTARIO | 14 ABISMO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Architecture / runtime / Git / CI | I,V,P | A,C | — | C | — | — | — | — | — | — | — | — | C | — |
| Data acquisition / adapters | I,V,P | A | D | C | — | V | V | — | — | — | D | — | V,P | — |
| Source-process / schema / revision integrity | I,V | A | D | C | A | V | — | — | — | — | — | — | V,P | — |
| Mathematics / statistical inference | — | A | D | C | D,A,V,P | A | A | A | A,V | A | A | A | V | A |
| Uncertainty / calibration | — | A | D | C | D,A,V,P | A | A | A | A,V | V | A | A | V | A,V |
| Temporal semantics / longitudinal inference | I | A | D | C | A,V | D,A,V,P | A | A | A,V | V | A | A | V | A |
| Regime / change detection | — | A | D | C | A,V | D,A,V | — | A | A | D,A,V,P | A | — | V | A |
| Spatial / population / denominator | I | A | D | C | A,V | A | D,A,V,P | A | A | A | A | A | V | A |
| Mobility / migration / transport | I | A | D | C | A,V | A | D,A,V,P | A | A | A | A | A | V | A |
| Network / dynamic coupling | I | A | D | C | A,V | A | A | D,A,V,P | A,V | A | A | A | V | A,V |
| Feedback / cascades / propagation | I | A | D | C | A,V | A | A | D,A,V,P | A,V | A,V | A | A | V | D,A,V,P |
| Forecasting / probabilistic prediction | I | A | D | C | A,V | A,V | A,V | A,V | D,A,V,P | V | A | A | V | A,V |
| Early warning / risk | I | A | D | C | A,V | A,V | A,V | A,V | A,V | D,A,V,P | A | D,A,V | V | A,V |
| Clinical / epidemiological interpretation | I | A | D | C | A | A | A | A | A | A | D,A,V,P | A | V | A |
| Environmental / climate / meteorology interpretation | I | A | D | C | A | A | A | A | A | A | D,A,V | A | V | A |
| Extreme events / tail risk | I | A | D | C | A,V | A | A | A,V | A,V | A,V | A | A | V | D,A,V,P |
| Causal inference | I | A | D | C | D,A,V | A | A | A,V | A | A | A,V | A | V,P | A |
| Epistemology / evidence / provenance | I | A | D | C | A | A | A | A | A | A | A | A | D,A,V,P | A |
| Decision / prevention / utility / VOI | I | A | D | C | A,V | A | A | A | A,V | A,V | A | D,A,V,P | V | A,V |
| Prospective evaluation / outcomes | I | A | D | C | A,V | A,V | A,V | A,V | D,A,V | D,A,V | A,V | A,V | D,A,V,P | A,V |

## Responsibility matrix

| Activity | Primary owner | Required collaborators | Persistence owner |
|---|---|---|---|
| Discover literature/data | BIBLIOTECARIO | ESPÍA, NOTARIO | BIBLIOTECARIO + NOTARIO |
| Define scientific question | ESPÍA | relevant specialist | ESPÍA |
| Formalize model/estimand | FORJA | ESPÍA + specialist | FORJA |
| Validate temporal semantics | CRONOS | NOTARIO + FORJA | CRONOS |
| Validate spatial/population semantics | ATLAS | MÉDICO + CRONOS + FORJA | ATLAS |
| Infer dynamic interactions | NEXO | FORJA + CRONOS + GROK | NEXO |
| Build/evaluate forecasts | ORÁCULO | FORJA + CRONOS + NEXO | ORÁCULO |
| Validate early warnings | CENTINELA | ORÁCULO + NOTARIO + GROK | CENTINELA |
| Validate health interpretation | MÉDICO | ESPÍA + ATLAS + CRONOS | MÉDICO |
| Stress extreme/tail behavior | ABISMO | FORJA + NEXO + CENTINELA | ABISMO |
| Evaluate decision value | ESTRATEGA | ORÁCULO + CENTINELA + NOTARIO | ESTRATEGA |
| Verify evidence/provenance | NOTARIO | BIBLIOTECARIO + GROK + ESPÍA | NOTARIO |
| Implement executable capability | INGENIERO | scientific owner + NOTARIO | INGENIERO |
| Adversarial challenge | GROK | capability owner | GROK + owner |
| Promote knowledge to Master State | NOTARIO | ESPÍA + capability owner | NOTARIO / Master State |

## Coverage audit

### Covered without requiring independent missions

- Data acquisition/data engineering: technically owned by INGENIERO; scientific acquisition semantics audited by ESPÍA/CRONOS/ATLAS/NOTARIO.
- Scientific computing: INGENIERO + FORJA.
- Mathematics/statistics/optimization: FORJA.
- Epidemiology/medicine/public health/environmental health: MÉDICO.
- Climate/meteorology: MÉDICO for domain interpretation, ESPÍA for integration, BIBLIOTECARIO for source discovery, INGENIERO for acquisition.
- Demography/migration/mobility: ATLAS.
- Economics/infrastructure/energy/water/maritime/public administration: no separate agent is justified at this stage; domain-specific evidence enters through BIBLIOTECARIO and is synthesized by ESPÍA, while technical acquisition belongs to INGENIERO. A dedicated mission should be created only if sustained independent methodology or validation burden emerges.
- Network science/causal inference: NEXO + FORJA + ESPÍA + NOTARIO.
- Forecasting: ORÁCULO.
- Early warning/risk: CENTINELA.
- Uncertainty: FORJA, with ORÁCULO/ABISMO downstream specialization.
- Extreme-event analysis: ABISMO.
- Decision science: ESTRATEGA.
- Epistemology/provenance: NOTARIO.
- Adversarial science: GROK.

### Deliberate non-fragmentation decisions

1. **No separate acquisition agent:** acquisition is inseparable from executable infrastructure and source contracts; INGENIERO owns implementation while scientific missions own semantics.
2. **No separate causal agent:** causal identification is too cross-cutting to isolate cleanly; FORJA provides formal inference, NEXO supplies dynamic mechanisms, MÉDICO supplies domain constraints, NOTARIO governs evidentiary claims, ESPÍA integrates.
3. **No separate climate/maritime/economics agents:** these are domain families whose scientific ownership becomes necessary only when a sustained independent model/validation pipeline exists.
4. **No separate uncertainty agent:** uncertainty is foundational statistics and propagates into forecasting, warning, tails and decisions; FORJA is the methodological owner.
5. **No separate risk agent:** risk is operationally coupled to event definition, warning performance and consequence; CENTINELA owns warning/risk methodology while ESTRATEGA owns decision utility.

## Coverage gaps to monitor

The architecture does not claim that a named mission makes a capability solved. The following remain project-level scientific frontiers requiring empirical evidence or engineering implementation:

- continuous real-source acquisition;
- measurement-process modelling;
- latent-state estimation;
- dynamic coupling identification;
- multisystem joint state;
- spatial and multiscale dynamics;
- full uncertainty propagation;
- scientifically validated regime detection;
- predictive cascade validation;
- operational early-warning validation;
- prediction-to-decision utility;
- prospective outcome evidence.

Mission ownership means **who must investigate**, not that the capability already exists.
