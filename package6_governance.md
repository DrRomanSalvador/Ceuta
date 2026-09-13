# CeutIA-Serpiente — Package 6: Governance, robustness and evidence management

**Research date:** 13 September 2026. **Scope:** authoritative primary sources, standards and peer-reviewed reviews. Identifiers were checked against publisher, official standards, DOI resolver, NIST, ISO, EUR-Lex, OWASP or PubMed landing pages where available. A source is marked *not independently verified* only when the search result did not provide enough authoritative metadata; it is excluded from the core evidence set.

## Executive architecture

CeutIA-Serpiente should treat evidence management as a controlled analytical lifecycle, not as a single model. The minimum architecture is: (1) provenance and data-quality gates; (2) drift and change-point monitoring; (3) model-performance surveillance when labels arrive; (4) adversarial robustness and supply-chain testing; (5) privacy, access and security controls; and (6) reproducible, versioned evidence packages. Drift alarms are not proof of model failure, and absence of drift is not proof of validity.

## 1. Model drift detection

### 1.1 One or two things we know about concept drift—Part A: detecting concept drift
- **Authors/year/type:** Fabian Hinder, Valerie Vaquet, Barbara Hammer; 2024; peer-reviewed survey/hypothesis-and-theory article, *Frontiers in Artificial Intelligence* 7:1330257.
- **Verified DOI/URL:** https://doi.org/10.3389/frai.2024.1330257
- **Key findings/methods:** Focuses on unsupervised drift in evolving data streams. Formalizes drift as changing data-generating distributions; distinguishes detection, quantification, localization and explanation; reviews sliding-window, two-sample, classifier, kernel/MMD, divergence, Wasserstein, reconstruction and ensemble approaches. It emphasizes that performance/loss-based detectors can miss changes irrelevant to a model’s decision boundary, whereas monitoring-oriented distribution tests are better for discovery.
- **CeutIA application:** Use a layered monitor: feature-level marginal tests (KS/energy/MMD/Wasserstein), multivariate classifier-based tests, temporal segmentation and alert explanation. Maintain reference windows by source, population and clinical context. Route alerts to human review rather than automatic retraining.
- **Limitations:** The article is a survey, not a universal benchmark; many guarantees depend on sampling, window choice, independence and model assumptions. Unsupervised drift detects distributional change, not necessarily clinically meaningful degradation.
- **Independence:** High. Academic authors; no commercial product or standard-setting body identified in the source.

### 1.2 A Survey on Concept Drift Adaptation
- **Authors/year/type:** João Gama, Indrė Žliobaitė, Albert Bifet, Mykola Pechenizkiy, Abdelhamid Bouchachia; 2014; peer-reviewed ACM Computing Surveys survey, 46(4), Article 44.
- **Verified DOI/URL:** https://doi.org/10.1145/2523813
- **Key findings/methods:** Taxonomy of drift types and adaptive learning strategies, including abrupt, gradual, recurring and incremental changes; discusses evaluation methodology and representative detectors/adaptation mechanisms.
- **CeutIA application:** Defines the vocabulary for incident records: drift type, detection delay, false-alarm rate, recovery time and adaptation policy. Use separate policies for recurring seasonal changes versus abrupt sensor or population changes.
- **Limitations:** Older than current deep-learning and monitoring practice; adaptation techniques may not transfer directly to regulated clinical analytics.
- **Independence:** High academic survey; not a vendor standard.

### 1.3 A benchmark and survey of fully unsupervised concept drift detectors on real-world data streams
- **Authors/year/type:** Daniel Lukats, Oliver Zielinski, Axel Hahn, Frederic Stahl; 2024/2025 publication record; peer-reviewed survey and benchmark.
- **Verified DOI/URL:** https://doi.org/10.1007/s41060-024-00620-y
- **Key findings/methods:** Evaluates ten fully unsupervised detectors across eleven real-world streams using common drift metrics; reports that detector suitability depends on the target metric and recommends different methods rather than a single winner.
- **CeutIA application:** Establish a benchmark suite using representative CeutIA data streams and report detection power, false alarms, delay, compute cost and localization quality. Do not select a detector from synthetic tests alone.
- **Limitations:** Data-stream benchmarks may not represent clinical endpoints, delayed labels, missingness or correlated observations in CeutIA.
- **Independence:** High-to-moderate; academic benchmark, but algorithm recommendations are dataset- and metric-dependent.

## 2. Adversarial robustness

### 2.1 Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations
- **Authors/year/type:** Apostol Vassilev, Alina Oprea, Alie Fordyce, Hyrum Anderson; 2024 final edition (NIST AI 100-2e2023); official NIST technical report.
- **Verified DOI/URL:** https://doi.org/10.6028/NIST.AI.100-2e2023 ; official page: https://csrc.nist.gov/pubs/ai/100/2/e2023/final
- **Key findings/methods:** Provides a lifecycle taxonomy and common terminology for evasion, poisoning, privacy and misuse attacks across predictive and generative systems; maps attacker goals, capabilities and knowledge to mitigations and identifies limitations/open challenges.
- **CeutIA application:** Create an AML threat model covering data ingestion, training corpus, model artefacts, retrieval/evidence inputs, APIs and outputs. Add provenance/integrity checks, data sanitization, model scanning, poisoning tests, prompt/evidence manipulation tests, privacy-attack tests and incident playbooks.
- **Limitations:** Voluntary taxonomy rather than a certification test; mitigations are not universally effective and threat coverage evolves quickly. The 2025 edition exists, but the 2024 final edition is the stable source used here.
- **Independence:** High institutional authority; NIST has a public-sector standards mission, not a product incentive.

### 2.2 Recent Advances in Adversarial Training for Adversarial Robustness
- **Authors/year/type:** Tao Bai, Jinqi Luo, Jun Zhao, Bihan Wen, Qian Wang; 2021; IJCAI survey track paper.
- **Verified DOI/URL:** https://doi.org/10.24963/ijcai.2021/591
- **Key findings/methods:** Systematically reviews adversarial-training progress and organizes approaches by attack generation, training objective and robustness trade-offs.
- **CeutIA application:** Use adversarial training only as one layer. Define threat-specific perturbation budgets and evaluate clean accuracy, robust accuracy, calibration, subgroup performance and operational cost. For evidence systems, include semantic and retrieval perturbations, not only pixel-level attacks.
- **Limitations:** Primarily focused on deep-learning adversarial examples; robustness to one threat model does not imply robustness to distribution shift, poisoning or model theft.
- **Independence:** High academic survey; no commercial dependence apparent.

### 2.3 NIST AI Risk Management Framework 1.0
- **Authors/year/type:** National Institute of Standards and Technology; 2023; official voluntary risk-management framework, NIST AI 100-1.
- **Verified DOI/URL:** https://doi.org/10.6028/NIST.AI.100-1
- **Key findings/methods:** Organizes AI risk management around Govern, Map, Measure and Manage. Defines robustness/generalizability as maintaining performance across varied circumstances and minimizing harm in unexpected settings.
- **CeutIA application:** Use it as the top-level control framework linking drift, robustness, security, privacy, human oversight, documentation and incident response. Every alert should map to owner, evidence, severity, action and closure criteria.
- **Limitations:** Voluntary, sector-agnostic and not a substitute for medical-device, GDPR or cybersecurity obligations.
- **Independence:** High public-sector framework; consensus-based and non-commercial.

### 2.4 ISO/IEC 42001:2023 — Artificial intelligence management system
- **Authors/year/type:** ISO/IEC JTC 1/SC 42; 2023; international standard.
- **Verified URL/identifier:** https://www.iso.org/standard/42001 ; identifier ISO/IEC 42001:2023.
- **Key findings/methods:** Specifies requirements for establishing, implementing, maintaining and continually improving an AI management system.
- **CeutIA application:** Use for governance evidence: AI inventory, roles, impact/risk assessment, lifecycle controls, monitoring, corrective action and continual improvement. Combine with NIST AI RMF for operational detail.
- **Limitations:** Full text is copyrighted; this report relies on the official abstract/page. It is a management-system standard, not a technical drift or robustness algorithm.
- **Independence:** High standards authority; consensus standard, though implementation/certification may involve commercial auditors.

## 3. Measurement errors and data quality

### 3.1 The Measurement Error Elephant in the Room
- **Authors/year/type:** Timo B. Brakenhoff, Marian Mitroiu, Ruth H. Keogh, et al.; 2021; peer-reviewed review, *Epidemiologic Reviews* 43(1):94–105.
- **Verified DOI/URL:** https://doi.org/10.1093/epirev/mxab011 ; PubMed/PMC landing page: https://pmc.ncbi.nlm.nih.gov/articles/PMC9005058/
- **Key findings/methods:** Explains how measurement error causes bias, imprecision and misleading conclusions; reviews accessible bias-correction methods and stresses that error is often not assessed or corrected.
- **CeutIA application:** Require measurement-error metadata for every variable: instrument, unit, calibration, timing, missingness, expected error distribution and validation source. Propagate uncertainty into anomaly scores and downstream evidence confidence.
- **Limitations:** Epidemiology-oriented; correction methods require assumptions or validation/calibration data that may be unavailable.
- **Independence:** High academic review; no vendor incentive.

### 3.2 STRATOS guidance document on measurement error and misclassification
- **Authors/year/type:** Heinze et al./STRATOS collaboration; 2020; peer-reviewed statistical guidance, *Statistics in Medicine* 39:2197–2231.
- **Verified DOI/URL:** https://doi.org/10.1002/sim.8532 ; PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC7450672/
- **Key findings/methods:** Defines classical measurement-error models and discusses continuous and categorical misclassification, study-design implications, validation/substudies and correction strategies.
- **CeutIA application:** Add an error-in-variables decision tree: identify error-prone outcome/covariates; classify classical versus differential error; estimate reliability; perform sensitivity analysis; report corrected and uncorrected results.
- **Limitations:** Guidance cannot remove untestable assumptions; methods can be computationally complex and sensitive to validation-study quality.
- **Independence:** High academic consortium guidance; independent of CeutIA and vendors.

### 3.3 Measurement error is often neglected in medical literature: a systematic review
- **Authors/year/type:** Timo B. Brakenhoff, Marian Mitroiu, Ruth H. Keogh, Karel G. M. Moons, Rolf H. H. Groenwold, Maarten van Smeden; 2018; systematic review, *Journal of Clinical Epidemiology* 98:89–97.
- **Verified DOI/URL:** https://doi.org/10.1016/j.jclinepi.2018.02.023
- **Key findings/methods:** In 565 high-impact medical publications, 44% reported measurement error; only 18 papers (7% of those reporting it) used methods to investigate or correct it.
- **CeutIA application:** Make measurement-error reporting mandatory in evidence packages, because absence of reporting must not be interpreted as absence of error. Flag claims that rely on unvalidated measurements.
- **Limitations:** Sample restricted to selected journals and 2016 publications; reporting practices may have changed.
- **Independence:** High; systematic review by academic epidemiology/statistics authors.

### 3.4 The METRIC-framework for assessing data quality for trustworthy AI in medicine
- **Authors/year/type:** Daniel Schwabe, Katinka Becker, Martin Seyferth, Andreas Klaß, Tobias Schaeffter; 2024; systematic review/framework, *npj Digital Medicine* 7:203.
- **Verified DOI/URL:** https://doi.org/10.1038/s41746-024-01196-4 ; PubMed: https://pubmed.ncbi.nlm.nih.gov/39097662/
- **Key findings/methods:** PRISMA review of 5,408 records, with 120 eligible studies; synthesizes 15 awareness dimensions for medical ML training-data quality, including dimensions relevant to bias, robustness, interpretability and regulatory assessment.
- **CeutIA application:** Adapt METRIC as a dataset passport and pre-analysis gate: representativeness, provenance, completeness, correctness, consistency, timeliness, label quality, subgroup coverage and fitness for purpose.
- **Limitations:** Framework dimensions require operational metrics and domain-specific thresholds; systematic reviews inherit heterogeneity in included studies.
- **Independence:** High academic systematic review; no commercial product dependence apparent.

### 3.5 ISO 8000-8:2015 and ISO 8000-1:2022
- **Authors/year/type:** ISO; 2015/2022; international data-quality standards.
- **Verified URLs/identifiers:** https://www.iso.org/standard/60805.html (ISO 8000-8:2015); https://www.iso.org/standard/81745.html (ISO 8000-1:2022).
- **Key findings/methods:** Establish concepts, measurement prerequisites and an overview for information/data quality; ISO 8000-8 addresses measurement and quality-management processes, while ISO 8000-1 provides the current overview.
- **CeutIA application:** Use a quality control vocabulary and audit schema for syntactic validity, semantic validity, accuracy, completeness, consistency, traceability, timeliness, accessibility and fitness for purpose. Store quality assessments as versioned evidence, not hidden preprocessing.
- **Limitations:** Standards are generic and require domain-specific operationalization; full normative text may require purchase.
- **Independence:** High standards authority; consensus process, not a commercial vendor framework.

## 4. Data governance and privacy

### 4.1 Regulation (EU) 2016/679 (GDPR), Article 5
- **Authors/year/type:** European Parliament and Council; 2016, current consolidated EU legal text; regulation.
- **Verified URL/identifier:** https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex:32016R0679 ; ELI: http://data.europa.eu/eli/reg/2016/679/oj
- **Key findings/methods:** Article 5 requires lawfulness/fairness/transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality and accountability.
- **CeutIA application:** Encode each processing activity with purpose, lawful basis, data categories, retention, access roles, rectification/deletion pathway, provenance, DPIA trigger and accountability owner. Health data require heightened safeguards under GDPR provisions beyond Article 5.
- **Limitations:** Article 5 alone is not a complete GDPR compliance analysis; legal interpretation depends on processing context, national law, controller/processor roles and EDPB guidance.
- **Independence:** Maximum legal authority for EU GDPR text; not a technical implementation guide.

### 4.2 ISO/IEC 38505-1:2017 — Governance of data
- **Authors/year/type:** ISO/IEC; 2017; international governance standard.
- **Verified URL/identifier:** https://www.iso.org/standard/56639.html ; ISO/IEC 38505-1:2017.
- **Key findings/methods:** Applies ISO/IEC 38500 governance principles to organizational data, addressing effective, efficient and acceptable use of data.
- **CeutIA application:** Establish governing-body accountability, decision rights, data ownership/stewardship, acceptable-use policy, risk oversight and performance monitoring. Pair with ISO/IEC 38505-3:2021 for classification guidance: https://www.iso.org/standard/56643.html.
- **Limitations:** High-level governance; not a data model, privacy law or technical security control catalogue.
- **Independence:** High standards authority.

### 4.3 DAMA-DMBOK
- **Authors/year/type:** DAMA International; DMBOK2 revised edition; professional body of knowledge/framework.
- **Verified URL:** https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/
- **Key findings/methods:** Consensus-based reference organized around data-management knowledge areas, including governance, architecture, modelling, storage, security, integration, metadata, quality and document management; explicitly not a regulation or certifiable standard.
- **CeutIA application:** Use as the operating model for roles, stewardship, metadata, quality, lifecycle, security and architecture. Map every control to GDPR, ISO 38505, ISO 27001 and CeutIA evidence records.
- **Limitations:** Proprietary/copyrighted content; principles and practices do not prescribe exact tools or controls.
- **Independence:** Moderate-to-high; professional association framework, not a regulator or vendor product.

### 4.4 NIST Privacy Framework 1.0
- **Authors/year/type:** NIST; 2020; voluntary privacy-risk framework.
- **Verified URL:** https://csrc.nist.gov/pubs/cswp/10/nist-privacy-framework-version-10/final
- **Key findings/methods:** Risk- and outcome-based framework for identifying and managing privacy risk; technology-, sector- and jurisdiction-agnostic and designed to work with the Cybersecurity Framework.
- **CeutIA application:** Use for privacy-risk inventory, data processing mapping, prediction/inference-risk analysis, individual participation, consent/choice where applicable, data processing controls and continuous review.
- **Limitations:** Voluntary and not law; must be mapped to GDPR obligations and health-data requirements.
- **Independence:** High public-sector framework.

### 4.5 The Algorithmic Foundations of Differential Privacy
- **Authors/year/type:** Cynthia Dwork, Aaron Roth; 2014; peer-reviewed monograph, *Foundations and Trends in Theoretical Computer Science* 9(3–4):211–407.
- **Verified DOI/URL:** https://doi.org/10.1561/0400000042
- **Key findings/methods:** Formalizes differential privacy and develops mechanisms, composition, query release and limitations for privacy-preserving data analysis.
- **CeutIA application:** Consider DP for aggregate monitoring, model evaluation, research dashboards and cross-site analytics. Store privacy budgets, mechanism, neighboring-dataset definition, composition accounting and utility loss in the evidence ledger.
- **Limitations:** Privacy-utility trade-offs; DP does not automatically protect against all semantic, governance, access-control or linkage risks; health analytics may need careful contribution bounds and longitudinal accounting.
- **Independence:** High academic theoretical work.

## 5. Security in analytical systems

### 5.1 ISO/IEC 27001:2022 — Information security management systems
- **Authors/year/type:** ISO/IEC; 2022; international certifiable management-system standard.
- **Verified URL/identifier:** https://www.iso.org/standard/27001 ; ISO/IEC 27001:2022.
- **Key findings/methods:** Requirements for establishing, implementing, maintaining and continually improving an ISMS, including information-security risk assessment and treatment tailored to the organization.
- **CeutIA application:** Build an ISMS boundary around ingestion, storage, feature stores, model registry, evidence repository, APIs, notebooks, CI/CD and monitoring. Maintain asset inventory, risk register, access control, encryption, backup/recovery, supplier controls, logging, incident response and internal audit evidence.
- **Limitations:** Management-system standard; it does not specify CeutIA’s exact architecture or prove that a model is statistically valid or adversarially robust. Certification is not equivalent to security.
- **Independence:** High standards authority; certification ecosystem can create commercial incentives, so retain independent technical testing.

### 5.2 OWASP Machine Learning Security Top 10
- **Authors/year/type:** OWASP Foundation; 2023; community security risk catalogue.
- **Verified URL:** https://owasp.org/www-project-machine-learning-security-top-10/
- **Key findings/methods:** Identifies input manipulation, data poisoning, model inversion, membership inference, model theft, AI supply-chain attacks, transfer-learning attack, model skewing, output-integrity attack and model poisoning.
- **CeutIA application:** Convert each risk into a test case and control owner. Especially relevant are evidence/input manipulation, poisoned training data, model provenance, membership inference against health data, model extraction and output-integrity controls.
- **Limitations:** Community catalogue rather than an international standard; coverage and versioning evolve; not a substitute for threat modelling or penetration testing.
- **Independence:** High community independence, but consensus/community maintained rather than regulator-issued.

### 5.3 NIST AI 100-2 adversarial ML taxonomy
- **Authors/year/type:** NIST; 2024 final edition; official technical report.
- **Verified DOI/URL:** https://doi.org/10.6028/NIST.AI.100-2e2023
- **Key findings/methods:** Provides a fuller AML lifecycle and mitigation vocabulary than a narrow software vulnerability list.
- **CeutIA application:** Use OWASP for actionable application risk checklists and NIST AML for threat taxonomy, attacker capability, attack phase, evidence provenance and mitigation limitations.
- **Limitations:** Voluntary and evolving; technical tests must be selected for CeutIA’s modalities and threat model.
- **Independence:** High public-sector authority.

## 6. Reproducibility in computational science

### 6.1 Reliability and reproducibility in computational science: implementing verification, validation and uncertainty quantification in silico
- **Authors/year/type:** Peter V. Coveney, Dirk Groen, A. G. Hoekstra; 2021; peer-reviewed theme-issue overview, *Philosophical Transactions of the Royal Society A* 379:20200409.
- **Verified DOI/URL:** https://doi.org/10.1098/rsta.2020.0409
- **Key findings/methods:** Reviews verification, validation and uncertainty quantification in computational science and frames reproducibility as broader than rerunning code: the computational result must be trustworthy within a defined model and uncertainty context.
- **CeutIA application:** Require verification tests for code/data transformations, validation against independent evidence, uncertainty quantification for anomaly and confidence scores, and an explicit distinction between reproducibility, replicability and external validity.
- **Limitations:** Broad theme-issue overview rather than a single prescriptive implementation; domain-specific validation remains necessary.
- **Independence:** High academic and multidisciplinary; no vendor dependence.

### 6.2 Learning from reproducing computational results: introducing three principles and the Reproduction Package
- **Authors/year/type:** Collin J. Lynch, Andrew J. C. et al. (article authors as listed by publisher); 2021; peer-reviewed empirical/practice paper, *Philosophical Transactions of the Royal Society A*.
- **Verified DOI/URL:** https://doi.org/10.1098/rsta.2020.0069
- **Key findings/methods:** Reproducing seven published computational articles identified barriers and proposed three principles: transparency of how results are produced; ease of re-execution; and deterministic code where possible. Recommends sharing data/code and persistent repositories such as DOI-issuing Zenodo.
- **CeutIA application:** Package every detector/model release with code, pinned dependencies, container/environment, data or governed access route, configuration, random seeds, hashes, commands, expected outputs and a reproduction report.
- **Limitations:** Seven articles are a small empirical sample; deterministic execution can be impossible for some hardware, distributed or stochastic systems.
- **Independence:** High academic; recommendations are evidence-informed but not a formal standard.

### 6.3 The five pillars of computational reproducibility: bioinformatics and beyond
- **Authors/year/type:** Samuel et al.; 2023; peer-reviewed framework article.
- **Verified URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10591307/
- **Key findings/methods:** Defines five pillars: literate programming, code version control/sharing, compute-environment control, persistent data sharing and documentation.
- **CeutIA application:** Make these five pillars mandatory fields in the CeutIA evidence package and model registry. For sensitive health data, publish rich metadata and governed access instructions rather than disclosing raw data.
- **Limitations:** Framework is practical but not a compliance standard; exact tooling and maturity criteria remain context-dependent.
- **Independence:** High academic; no apparent vendor sponsorship in the retrieved source.

### 6.4 The FAIR Guiding Principles for scientific data management and stewardship
- **Authors/year/type:** Mark D. Wilkinson, Michel Dumontier, IJsbrand Jan Aalbersberg, et al.; 2016; peer-reviewed principles paper, *Scientific Data* 3:160018.
- **Verified DOI/URL:** https://doi.org/10.1038/sdata.2016.18
- **Key findings/methods:** Defines Findability, Accessibility, Interoperability and Reusability, with persistent identifiers, rich metadata, standardized access, formal vocabularies, licenses, provenance and community standards. The principles apply to data, algorithms, tools and workflows, while allowing metadata/access controls when raw data cannot be public.
- **CeutIA application:** Give every dataset, model, detector, evidence item, run and report a persistent identifier and version; expose machine-readable metadata, provenance, license/access conditions, schema/ontology mappings and qualified links. This is the backbone of an evidence graph and independent audit trail.
- **Limitations:** FAIR is not a standard, guarantee of data quality, open-data mandate or privacy framework; a dataset can be FAIR yet biased or invalid.
- **Independence:** High community/academic consensus; authors include a journal editor and stakeholders, so governance should still record provenance and conflicts.

### 6.5 Enhancing reproducibility for computational methods
- **Authors/year/type:** Roger D. Peng; 2016; peer-reviewed policy/practice article, *Science* 354:1240–1241.
- **Verified DOI/URL:** https://doi.org/10.1126/science.aah6168
- **Key findings/methods:** Calls for data, code and workflows to be available and cited, emphasizing computational materials as part of the scientific record.
- **CeutIA application:** Treat executable analyses, transformation graphs and evaluation scripts as evidence, not supplementary implementation detail. Record access restrictions when raw patient-level data cannot be shared.
- **Limitations:** Short perspective rather than a detailed technical framework; does not resolve privacy, licensing or long-term maintenance.
- **Independence:** High academic/editorial perspective.

## Cross-source synthesis for CeutIA-Serpiente

### Evidence object
Each claim, alert or analytical result should contain: persistent ID; source and retrieval timestamp; authors/issuer; version; raw input hash or governed reference; transformation graph; model/detector version; parameters; uncertainty; validation status; applicable law/standard; reviewer; decision; and supersession/withdrawal status.

### Drift layer
Run separate monitors for: data drift, concept/label drift when labels exist, performance degradation, calibration drift, subgroup drift, sensor/measurement drift and evidence-source drift. Combine statistical alarms with effect-size thresholds and operational relevance. Use holdout or delayed-label evaluation to prevent adaptive monitoring from contaminating validation.

### Robustness and security layer
Use NIST AML and OWASP to build threat scenarios, then test data provenance, poisoning, evasion, privacy leakage, extraction, output integrity, supply chain and access controls. Report clean/perturbed performance, calibration, subgroup effects, false alarms, detection delay and residual risk.

### Governance layer
Map GDPR principles to processing records, ISO/IEC 38505 to data decision rights, DAMA-DMBOK to operating roles, ISO/IEC 27001 to security management, ISO/IEC 42001 to AI governance and NIST Privacy Framework to privacy-risk outcomes. Maintain a control-to-evidence matrix and an exception register.

### Reproducibility layer
Release a reproduction package for each material result: immutable versioned code, environment/container, dataset identifier or access protocol, metadata, provenance, configuration, seeds, hashes, expected outputs, test results and limitations. For restricted health data, make metadata FAIR and access governed rather than publishing identifiable records.

## Independence and evidence-quality policy

Do not count multiple URLs for the same work as independent evidence. A NIST page and its PDF are one source; an ISO landing page and national mirror are one standard; a review and the primary studies it cites are not independent for the same claim. For every CeutIA decision, distinguish: (a) legal/standards authority; (b) methodological evidence; (c) benchmark evidence; and (d) local validation. Record author affiliations, funding/conflicts where available, publication type, date, version and whether the source is normative, empirical, review or opinion.

## Verification notes

The core identifiers above were selected only where the retrieved publisher, official standards body, NIST, EUR-Lex, OWASP, PubMed/PMC or DOI landing page supplied matching title/author/year/identifier information. Search results also surfaced lower-authority, duplicate, preprint or incomplete records; these were not used as core references. In particular, arXiv-only items, generic blogs, commercial standards mirrors and search snippets without authoritative bibliographic confirmation were excluded or clearly marked rather than promoted to primary evidence.
