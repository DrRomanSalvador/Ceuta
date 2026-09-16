# BIBLIOGRAPHY / AUTHORITATIVE SOURCE MANIFEST 001

**Status:** ACTIVE — ESPÍA DEEP EXTRACTION
**Owner:** ESPÍA
**Scope:** CeutIA + SERPIENTE
**Purpose:** versioned inventory of recoverable scientific literature, standards, methodological sources and authoritative data/technical sources materially identified during the current deep-extraction mission.

## 1. Coverage statement

This manifest covers the scientific and authoritative source surfaces recoverable from the current CeutIA repository state, the existing scientific audit/handoff documents, the previously persisted ESPÍA scientific context, and primary/authoritative sources recovered during this mission.

It does **not** claim to be a universal literature search across all science. No complete external bibliography file was present in the repository before this mission. That absence is recorded as provenance/epistemological debt rather than silently treated as completeness.

## 2. Scientific literature / standards

| ID | Source | Class | Primary/secondary | Material use | State |
|---|---|---|---|---|---|
| BIB-001 | Collins et al. TRIPOD+AI, BMJ 2024;385:e078378. DOI 10.1136/bmj-2023-078378 | Guideline | Guideline | Prediction-study reporting, transparency, applicability, fairness | Integrated normatively; not validation |
| BIB-002 | Moons et al. PROBAST Explanation and Elaboration, Ann Intern Med 2019;170:1. DOI 10.7326/M18-1377 | Method/guidance | Methodological primary | Risk of bias and applicability appraisal | Integrated conceptually; not a score |
| BIB-003 | W3C PROV-O Recommendation, 2013 | Standard | Normative primary | Provenance entities, activities, agents, derivation and timing | Partially integrated; serialization gap remains |
| BIB-004 | Scheffer et al. Early-warning signals for critical transitions, Nature 2009;461:53–59. DOI 10.1038/nature08227 | Theory/synthesis | Primary scientific synthesis | Conditional early-warning mechanisms | Scientific reference only; not catastrophe prediction |
| BIB-005 | Dakos et al. Methods for detecting early warnings of critical transitions, PLOS ONE 2012;7:e41010. DOI 10.1371/journal.pone.0041010 | Method | Primary | EWS estimation/testing, moving-window indicators | Experimental/reference; real-time validation absent |
| BIB-006 | Early warning signals of infectious disease transitions: a review, 2021. PMCID PMC8479360; PMID 34583561 | Review | Secondary | Epidemiological EWS, data limitations and validation pathway | Reference; transportability not established |
| BIB-007 | Gneiting, Balabdaoui & Raftery. Probabilistic forecasts, calibration and sharpness, JRSS-B 2007;69:243–268. DOI 10.1111/j.1467-9868.2007.00587.x | Theory/method | Primary | Calibration, sharpness and proper forecast evaluation | Partially integrated |
| BIB-008 | Vickers & Elkin. Decision curve analysis, Med Decis Making 2006;26:565–574. DOI 10.1177/0272989X06295361 | Method | Primary | Decision-utility evaluation | Candidate; decision layer not validated |
| BIB-009 | Heath et al. Simulating Study Data to Support EVSI Calculations, Med Decis Making 2022;42:2. DOI 10.1177/0272989X211026292 | Method | Primary | Expected value of sample information | Candidate; no autonomous VOI engine established |

## 3. Authoritative data / technical sources recovered

These are not empirical corroboration of CeutIA/SERPIENTE claims. They are acquisition/source candidates whose provenance, revision, cadence, coverage and observation process must be preserved.

| ID | Source | Role | Relevant semantics | Current status |
|---|---|---|---|---|
| DATA-001 | AEMET OpenData / AEMET API | Meteorological and climatological observations | station identity, observation/product time, provisional/revision semantics, API availability | Acquisition opportunity verified; production contract must preserve vintages/revisions |
| DATA-002 | INE population and migration statistics | Population and migration denominators/flows | reference period, statistical definition, resident vs migration population | Authoritative source identified; temporal cadence and denominator semantics must remain explicit |
| DATA-003 | ECDC surveillance / infectious-disease data | Epidemiological surveillance | disease definition, reporting process, revision and surveillance coverage | Source identified; disease-specific contracts required |
| DATA-004 | INGESA / HUCE official activity and capacity information | Healthcare demand/capacity observations | daily publication, source process, population stratification, occupancy/activity definitions | Authoritative current source identified; publication and revision semantics required |
| DATA-005 | MITECO air-quality information and national evaluation reports | Environmental exposure/air-quality observations | station, pollutant, sampling/coverage and assessment period | Authoritative source identified; station/process continuity required |
| DATA-006 | Autoridad Portuaria de Ceuta / official port statistics | Maritime/port flows | vessel/passenger/cargo definitions, period and throughput denominator | Authoritative acquisition candidate; continuous contract not yet established |

## 4. Source-dependence rules

A publication, dataset, technical report or official statement is not independent evidence merely because it has a different title or publisher surface.

The manifest must preserve, when recoverable:

- upstream dataset/source;
- author/source dependence;
- methodological dependence;
- model dependence;
- revision/vintage dependence;
- derived-data lineage.

Three publications based on the same dataset are not counted as three independent empirical replications.

## 5. Primary-source recovery policy

Secondary reviews remain useful for discovery and synthesis. When a cited primary source is recoverable and could change an architectural, methodological or validation conclusion, the primary source takes precedence for extraction.

Guidelines and standards are normative/methodological evidence, not empirical proof of system validity.

Technical/API documentation establishes source availability and interface semantics, not scientific validity of downstream claims.

## 6. Current corpus closure state

`SCIENTIFIC_LITERATURE_RECOVERABLE_AND_DEEP_EXTRACTED = PARTIALLY_CLOSED`

The nine material scientific/standard sources listed above have been deeply extracted into `BIBLIOGRAPHY_DEEP_EXTRACTION_001`.

`AUTHORITATIVE_DATA_SOURCE_INVENTORY = IDENTIFIED`

The six authoritative data-source classes above have been identified and their scientific acquisition implications recorded. They are not yet equivalent to continuously validated production ingestion.

`UNIVERSAL_EXTERNAL_LITERATURE_EXHAUSTIVENESS = NOT_ESTABLISHED`

This state remains explicit because the repository did not contain a complete external bibliography manifest and a universal literature search has not been performed.

## 7. Scientific fixed-point boundary

Within the currently recoverable corpus, no additional bibliographic integration is justified merely by adding more models or references. Remaining material work is empirical/engineering or requires additional external evidence:

1. reconcile the canonical prediction-evaluation record with TRIPOD+AI/PROBAST without creating a duplicate contract;
2. close PIT semantic-state/consumer enforcement;
3. complete outcome ascertainment semantics;
4. establish prospective evaluation registration and real prospective outcomes;
5. reconcile source-process drift handling with the authoritative acquisition contracts;
6. build interaction-ready synchronized observations with denominator and observation-process semantics;
7. validate early-warning methods prospectively for explicitly defined targets and lead times;
8. establish decision-utility/VOI only when an authorized decision context and utility structure exist;
9. retain all catastrophe/collapse capabilities as bounded research until system-specific prospective evidence exists.

No production claim of universal catastrophe prediction, causal interaction identification, intervention effectiveness or autonomous scientific truth authority is supported by this corpus.
