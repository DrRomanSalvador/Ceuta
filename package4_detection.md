# CeutIA-Serpiente: Evidence Base for Detection Methods (Package 4)

**Research Date:** September 13, 2026  
**Project:** CeutIA-Serpiente — Epistemic-analytical system for evidence management and anomaly detection  
**Analytical Layer Focus:** Anomaly detection, regime change, weak signal detection, alerting

## Executive Summary

### Key findings by topic

**1. Anomaly Detection**
- Statistical methods (STL + z-score, ARIMA) can outperform ML/DL for point anomalies in univariate time series.
- Extended Isolation Forest (EIF) is a strong default candidate for multivariate tabular data.
- Autoencoders are useful for unsupervised detection of complex patterns.

**2. Regime Change Detection**
- PELT is a strong offline method for multiple change points.
- CUSUM is suited to real-time monitoring of mean shifts.
- BOCPD provides probabilistic change-point estimates over time.

**3. Weak Signal Detection**
- Critical-slowing-down indicators such as AR(1), variance and DFA can provide early-warning information for some critical transitions.
- LRao combines a learned nonlinear transformation with Rao detection for non-Gaussian noise settings.
- Durbin-Watson-based approaches can detect weak periodic signals under particular noise assumptions.

**4. Signal Detection Theory**
- d' separates detector discriminability from decision criterion.
- ROC curves characterize the sensitivity/specificity trade-off over thresholds.
- d' = z(hit rate) − z(false alarm rate), subject to the usual SDT assumptions and numerical handling of extreme rates.

**5. False Positives / False Negatives**
- Youden's J (J = Se + Sp − 1) is a balanced default threshold criterion when false-positive and false-negative costs are treated symmetrically.
- Cost-sensitive thresholding is required when consequences are asymmetric.
- Continuous monitoring of FPR/FNR is necessary to detect alert fatigue and performance degradation.

## Design principles for Serpiente

| Layer | Candidate method | Rationale |
|---|---|---|
| Anomaly detection | EIF + autoencoder ensemble | Multivariate robustness plus complex-pattern detection |
| Regime change | PELT offline + CUSUM real time | Retrospective multiple-change detection plus fast sequential monitoring |
| Weak signals | AR(1), variance, DFA | Early-warning indicators for mechanisms where critical slowing down applies |
| Alert threshold | Youden J by default + cost-sensitive thresholding | Balanced baseline with explicit asymmetric-cost support |
| FPR/FNR management | Continuous monitoring + recalibration | Controls alert fatigue and adapts to distributional change |

## Limitations identified

1. Healthcare validation: much of the evidence originates in engineering, finance or ecology.
2. Multivariate data: several methods rely on univariate assumptions or require separate multivariate validation.
3. Real-time performance: computational efficiency is not systematically established across all candidate methods.
4. Interpretability: deep-learning detectors require explicit explanation and attribution mechanisms.
5. Non-stationarity: static thresholds can fail under changing data-generating processes; adaptive or online calibration requires validation.

## Evidence Base

The research package contains more than 30 sources, with DOI/URL verification where available, together with independence and applicability assessments for the CeutIA-Serpiente analytical layer.

### Topic 1 — Anomaly Detection Methods

#### 1.1 Deep Learning for Time Series Anomaly Detection: A Survey

**Authors:** Zahra Zamanzadeh Darban, Geoffrey I. Webb, Shirui Pan, Charu C. Aggarwal, Mahsa Salehi  
**Year:** 2024 arXiv version; ACM Computing Surveys publication 2025  
**Type:** Peer-reviewed survey  
**DOI:** 10.1145/3691338  
**URL:** https://arxiv.org/abs/2211.05244

**Key findings:** Taxonomy of reconstruction, prediction, hybrid and representation-learning approaches. Deep learning is particularly relevant to contextual and collective anomalies, while computational cost and interpretability remain limitations.

**CeutIA application:** Autoencoders and temporal prediction models are candidates for multivariate physiological and surveillance streams where temporal context matters.

**Limitations:** Training-data requirements, low-prevalence anomaly regimes and interpretability constraints.

**Independence:** Independent academic research.

#### 1.2 Anomaly Detection in Univariate Time-series: A Survey on the State-of-the-Art

**Authors:** Mohammad Braei, Sebastian Wagner  
**Year:** 2020  
**Type:** Survey / preprint  
**DOI:** 10.48550/arXiv.2004.00433  
**URL:** https://arxiv.org/abs/2004.00433

**Key findings:** Comparison of statistical, classical ML and deep-learning methods. Statistical methods can be competitive or superior for point and continuous anomalies in univariate settings, with lower computational cost.

**CeutIA application:** Supports a staged detector architecture in which inexpensive statistical screening precedes more complex models when contextual structure warrants them.

**Limitations:** Primarily univariate and largely non-healthcare benchmark data.

**Independence:** Independent academic research.

#### 1.3 Unsupervised Machine Learning for Anomaly Detection: A Systematic Review

**Year:** 2025  
**Type:** Systematic literature review  
**URL:** https://www.internationaljournalssrg.org/IJEEE/paper-details?Id=1095

**Key findings:** Autoencoders, Isolation Forest and LSTM-autoencoder approaches are recurring unsupervised methods across heterogeneous application domains. Evaluation protocols vary substantially.

**CeutIA application:** Supports ensemble detection and explicit metric governance rather than treating one algorithm as universally optimal.

**Limitations:** Heterogeneous protocols and limited operational analysis of false-positive burden.

**Independence:** Systematic review.

#### 1.4 Evaluating Unsupervised Anomaly Detection

**Authors:** Dominik Olszewski et al. (ANOMALY-1 study)  
**Year:** 2026  
**Type:** Empirical benchmark  
**URL:** https://www.scribd.com/document/796594146/23-0570

**Key findings:** Reported large-scale comparison across 33 algorithms and 52 real-world datasets; EIF is reported as a strong performer for multivariate tabular data and k-NN for some local-anomaly settings.

**CeutIA application:** Candidate baseline for multivariate tabular anomaly detection, subject to independent healthcare validation.

**Limitations:** Tabular focus; source status and peer-review status require explicit tracking rather than treating the result as settled clinical evidence.

**Independence:** Benchmark research; not equivalent to healthcare validation.

### Topic 2 — Regime Change / Change Point Detection

#### 2.1 Selective Review of Offline Change Point Detection Methods

**Authors:** Charles Truong, Laurent Oudre, Nicolas Vayatis  
**Year:** 2020  
**Type:** Peer-reviewed survey  
**DOI:** 10.1016/J.SIGPRO.2019.107299

**Key findings:** Organizes change-point detection around cost functions, search methods and constraints on the number of changes. PELT provides an important computationally efficient exact-search framework under suitable conditions; CUSUM is foundational for sequential mean-shift detection; BOCPD provides posterior run-length/change information.

**CeutIA application:** PELT for retrospective analysis, CUSUM for sequential monitoring and Bayesian methods where probabilistic change information is useful.

**Limitations:** Dependence, autocorrelation and penalty selection require domain-specific handling.

**Independence:** Independent academic survey.

#### 2.2 Comprehensive Analysis of Change-Point Dynamics Detection in Time Series Data: A Review

**Year:** 2024  
**Type:** Review  
**URL:** https://www.sciencedirect.com/science/article/abs/pii/S0957417424002070

**Key findings:** Reviews changes in mean, variance, trend and correlation structure and contrasts exact and approximate approaches, including deep-learning methods.

**CeutIA application:** Supports monitoring multiple dimensions of regime change rather than reducing regime detection to mean shifts.

**Limitations:** Real-time performance and healthcare transferability require independent validation.

#### 2.3 Deep Learning-Driven Regime Switching Models for Capturing Structural Breakpoints in Financial Markets

**Year:** 2026  
**Type:** Research article  
**URL:** https://fupubco.com/futech/article/view/815

**Key findings:** Combines recurrent neural networks, Markov regime switching, attention and adaptive volatility modeling for structural-break detection in financial data.

**CeutIA application:** Provides a candidate architecture for complex multivariate regime shifts, not a validated healthcare method.

**Limitations:** Financial-domain evidence, computational cost and domain-transfer uncertainty.

#### 2.4 Change Point Detection: When Did the Metric Shift?

**Year:** 2026  
**Type:** Technical guide  
**URL:** https://www.statstest.com/change-point-detection-when-metric-shifted

**Key findings:** Practical implementation guidance for PELT, CUSUM and Bayesian online change-point detection, with emphasis on validating detected changes against known events.

**CeutIA application:** Useful implementation guidance but should be ranked below primary methodological evidence.

**Limitations:** Tutorial-level evidence.

### Topic 3 — Weak Signal Detection

#### 3.1 Early Warning Signals in Ecological Time-Series

**Authors:** Roberto Alvarez-Martinez, Pedro Miramontes  
**Year:** 2026  
**Type:** Peer-reviewed review  
**DOI:** 10.3390/e28060628  
**URL:** https://esd.copernicus.org/articles/15/1117/2024/esd-15-1117-2024.html

**Key findings:** Critical slowing down can be associated with rising lag-1 autocorrelation, increasing variance and spectral reddening before some bifurcation-driven transitions. The review distinguishes bifurcation-, noise-, rate- and shock-induced tipping mechanisms.

**CeutIA application:** AR(1), variance and DFA can form a weak-signal layer, but only when the hypothesized transition mechanism supports their interpretation.

**Limitations:** Requires appropriate temporal resolution and sufficient observations; indicators are mechanism-dependent and can generate false positives under other tipping mechanisms.

#### 3.2 Detection of Weak Signals Under Arbitrary Noise Distributions

**Year:** 2026  
**Type:** arXiv preprint  
**URL:** https://arxiv.org/abs/2603.01737

**Key findings:** Proposes a neural-network-assisted Rao detection framework for non-Gaussian noise.

**CeutIA application:** Candidate detector for low-SNR signals when the noise distribution violates simple Gaussian assumptions.

**Limitations:** Preprint status and validation mainly in engineering/physics domains; requires suitable noise-only data.

#### 3.3 Weak Signal Detection Technique Based on Durbin–Watson Test and One-Bit Sampling

**Year:** 2024  
**Type:** Peer-reviewed research  
**DOI:** 10.1063/5.0198084

**Key findings:** Uses first-order autocorrelation and one-bit sampling to detect weak periodic signals under particular noise conditions.

**CeutIA application:** Candidate low-compute detector for weak periodic physiological or sensor signals.

**Limitations:** Assumption-dependent; reported SNR performance should not be transferred directly to healthcare without validation.

#### 3.4 Effectiveness of Early Warning Systems in the Detection of Infectious Diseases Outbreaks: A Systematic Review

**Year:** 2022  
**Type:** Systematic review  
**DOI:** 10.1186/s12889-022-14625-4

**Key findings:** Pre-diagnosis and syndromic surveillance data can provide earlier warning than confirmed diagnostic surveillance; effective systems commonly combine multiple data sources.

**CeutIA application:** Supports multi-source surveillance and early-warning architectures rather than reliance on one indicator.

**Limitations:** Heterogeneous designs and setting-specific transferability.

### Topic 4 — Signal Detection Theory

#### 4.1 Signal Detection Theory and Psychophysics

**Authors:** David M. Green, John A. Swets  
**Year:** 1966  
**Type:** Foundational book  
**Publisher:** Wiley

**Key findings:** Establishes the separation between discriminability and response criterion. d' quantifies separation between signal and noise distributions, while ROC analysis characterizes threshold-dependent trade-offs.

**CeutIA application:** Use SDT to distinguish detector capability from policy-selected alert thresholds.

**Limitations:** Classical formulations rely on distributional assumptions that may require extension for modern non-Gaussian, dependent or highly imbalanced data.

#### 4.2 Signal Detection Theory — d′, the Decision Criterion & ROC

**Year:** 2026  
**Type:** Educational tutorial  
**URL:** https://www.cogn-iq.org/learn/theory/signal-detection-theory/

**Key findings:** Practical explanation of d', criterion and ROC interpretation.

**CeutIA application:** Implementation-oriented reference for SDT metrics.

**Limitations:** Tutorial-level rather than primary methodological evidence.

#### 4.3 Signal Detection: Applying Analysis Methods from Psychology to Animal Behaviour

**Year:** 2020  
**Type:** Peer-reviewed methods paper  
**DOI:** 10.1098/rspb.2020.0329  
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7331002/

**Key findings:** Demonstrates SDT and ROC analysis in ecological decision contexts outside classical psychophysics.

**CeutIA application:** Supports SDT as a general framework for decisions under uncertain signal/noise separation.

#### 4.4 ROC Curve Analysis in Medical Research

**Year:** 2026  
**Type:** Technical guide  
**URL:** https://statclinic.net/blog/roc-curve-analysis-diagnostic-test-accuracy-in-medical-research/

**Key findings:** Covers ROC analysis, Youden's J and cost-sensitive threshold selection in medical contexts.

**CeutIA application:** Candidate implementation guidance for threshold analysis.

**Limitations:** Tutorial-level evidence.

### Topic 5 — False Positives and False Negatives in Surveillance

#### 5.1 Output-Based Methodological Approaches for Substantiating Freedom from Infection

**Authors:** Eleftherios Meletis et al.  
**Year:** 2024  
**Type:** Peer-reviewed review  
**DOI:** 10.3389/fvets.2024.1337661  
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10977073/

**Key findings:** Defines surveillance sensitivity/specificity and illustrates how false-negative risk and surveillance cost interact. Predictive quantities depend on prevalence assumptions.

**CeutIA application:** Useful conceptual framework for surveillance sensitivity, specificity and consequence-weighted monitoring.

**Limitations:** Veterinary epidemiology context; some assumptions may not hold in general decision systems.

#### 5.2 Sensitivity, Specificity, Positive Predictive Value, and Negative Predictive Value

**Year:** 2021  
**Type:** Educational/peer-reviewed review  
**DOI:** 10.1097/GRF.0000000000000617  
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC8156826/

**Key findings:** Establishes sensitivity, specificity, PPV and NPV and emphasizes prevalence dependence of predictive values.

**CeutIA application:** Foundational metrics for detector evaluation and alert-policy calibration.

#### 5.3 False Positive Rate Explained: A Complete Guide for ML Teams

**Year:** 2026  
**Type:** Technical guide  
**URL:** https://www.openlayer.com/blog/false-positive-rate-complete-guide-ml-teams

**Key findings:** Defines FPR, ROC trade-offs and production-oriented threshold monitoring.

**CeutIA application:** Operational reference for alert fatigue and FPR drift monitoring.

**Limitations:** Commercial technical guide; lower evidentiary authority than peer-reviewed methodological literature.

#### 5.4 Youden's J Index for ROC Threshold Selection

**Year:** 2026  
**Type:** Methodological guide  
**URL:** https://casrai.org/guides/youdens-j-index-roc-threshold-selection

**Key findings:** J = sensitivity + specificity − 1. Maximization corresponds to a balanced criterion; asymmetric costs require alternative threshold rules.

**CeutIA application:** Suitable as a documented default only where symmetric error costs are justified; otherwise use explicit cost-sensitive optimization.

**Limitations:** Binary classification and continuous-score assumptions; threshold uncertainty should be quantified.

#### 5.5 Diagnostic Decision Logic

**Year:** 2025  
**Type:** Educational resource  
**URL:** https://www.varsitytutors.com/practice/subjects/eppp-knowledge/lessons/diagnostic-decision-logic

**Key findings:** Explains sensitivity/specificity trade-offs, SDT and screening-versus-confirmation threshold logic.

**CeutIA application:** Supports multi-stage detection designs in which an initial sensitive detector is followed by more specific confirmation.

**Limitations:** Educational resource; not primary evidence.

## Cross-Source Synthesis

### Anomaly detection

The evidence supports a heterogeneous detector stack rather than a single universal algorithm. Classical statistical methods are appropriate baselines for simple univariate point anomalies. EIF is a candidate baseline for multivariate tabular anomalies. Autoencoders and temporal deep-learning methods become more relevant when anomalies are contextual, collective or strongly sequence-dependent. The repository should therefore treat method selection as conditional on data structure and anomaly class, not as a fixed algorithmic truth.

### Regime change

Offline and online detection are distinct operational problems. PELT is appropriate for retrospective segmentation under suitable cost/penalty assumptions; CUSUM is suited to sequential monitoring of specified changes; BOCPD is useful where posterior uncertainty over change timing is required. Multivariate and structural regime changes require additional validation rather than assuming a univariate mean-shift detector is sufficient.

### Weak signals

Weak-signal indicators must be tied to a causal/mechanistic hypothesis about the transition being monitored. Critical-slowing-down indicators should not be interpreted as generic predictors of every transition. Alternative tipping mechanisms can produce different or absent precursors. This is particularly important for CeutIA because an early-warning signal is an epistemic claim, not merely a high detector score.

### Signal detection and threshold policy

SDT provides a clean separation between detector discriminability and the policy used to issue alerts. ROC analysis should be used to characterize threshold behavior, while threshold selection must explicitly encode consequences, prevalence assumptions and operational capacity. Youden's J is a baseline criterion under symmetric costs, not a universal optimum.

### False-positive / false-negative governance

Serpiente should persist confusion-matrix metrics, prevalence assumptions, threshold values, confidence/uncertainty intervals, alert volume and downstream consequences. FPR/FNR should be monitored longitudinally because a detector can retain nominal performance while operational burden or miss costs change as the environment changes.

## Evidence Quality and Independence Policy

The evidence base should distinguish:

1. **Primary methodological evidence:** peer-reviewed methods papers, foundational texts and validated benchmark studies.
2. **Systematic reviews:** secondary evidence used to map the state of the field and identify convergent findings.
3. **Benchmarks:** empirical comparative evidence whose dataset composition and evaluation protocol must be retained.
4. **Healthcare/operational evidence:** evidence directly addressing clinical, public-health or operational surveillance contexts.
5. **Technical/tutorial sources:** implementation guidance, ranked below primary and systematic evidence.
6. **Preprints:** retained as emerging evidence but explicitly marked as not peer-reviewed where applicable.

Multiple URLs resolving to the same underlying work do not constitute independent evidence. Claims should retain source identity, publication status, domain, validation population, method assumptions and limitations.

## Proposed Evidence Object Fields

For each source or method evidence item, retain at minimum:

- persistent identifier;
- title and authors/issuer;
- publication date and retrieval timestamp;
- publication status;
- source type and evidence tier;
- DOI or canonical URL;
- dataset/domain and validation population;
- algorithm/method and assumptions;
- reported metrics and uncertainty;
- transformation or preprocessing requirements;
- implementation/version where relevant;
- CeutIA applicability assessment;
- limitations and transfer-risk notes;
- independence/correlation assessment;
- reviewer and verification status;
- supersession/withdrawal status.

## Limitations and Future Work

1. Validate candidate detectors on healthcare and public-health surveillance datasets.
2. Benchmark multivariate and temporal extensions under realistic missingness, autocorrelation and non-stationarity.
3. Measure real-time latency and computational cost under production-like workloads.
4. Add explicit explainability and attribution for deep-learning detectors.
5. Implement adaptive thresholding only after prospective calibration and drift validation.
6. Evaluate detector ensembles for correlated errors rather than assuming ensemble diversity.
7. Quantify operational alert burden, downstream actionability and consequence-weighted error.
8. Distinguish detector uncertainty from uncertainty about the underlying phenomenon and from uncertainty in the reference labels.

## References

1. Darban ZZ, et al. Deep Learning for Time Series Anomaly Detection: A Survey. ACM Computing Surveys. 2025. DOI: 10.1145/3691338.
2. Braei M, Wagner S. Anomaly Detection in Univariate Time-series: A Survey on the State-of-the-Art. arXiv:2004.00433. 2020.
3. Truong C, Oudre L, Vayatis N. Selective review of offline change point detection methods. Signal Processing. 2020;167:107299. DOI: 10.1016/J.SIGPRO.2019.107299.
4. Alvarez-Martinez R, Miramontes P. Early Warning Signals in Ecological Time-Series. Entropy. 2026;28(6):628. DOI: 10.3390/e28060628.
5. Green DM, Swets JA. Signal Detection Theory and Psychophysics. Wiley; 1966.
6. Meletis E, et al. Review state-of-the-art of output-based methodological approaches for substantiating freedom from infection. Frontiers in Veterinary Science. 2024;11:1337661. DOI: 10.3389/fvets.2024.1337661.
7. Olszewski D, et al. Evaluating Unsupervised Anomaly Detection. 2026. ANOMALY-1 study.
8. StatClinic. ROC Curve Analysis in Medical Research. 2026.
9. CASRAI. Youden's J Index for ROC Threshold Selection. 2026.
10. Hinder F, Vaquet V, Hammer B. One or two things we know about concept drift—Part A: detecting concept drift. Frontiers in Artificial Intelligence. 2024. DOI: 10.3389/frai.2024.1330257.
11. Gama J, Žliobaitė I, Bifet A, Pechenizkiy M, Bouchachia A. A Survey on Concept Drift Adaptation. ACM Computing Surveys. 2014. DOI: 10.1145/2523813.
12. Lukats D, Zielinski O, Hahn A, Stahl F. Benchmark/survey on change-point and drift detection. 2024/2025. DOI: 10.1007/s41060-024-00620-y.
13. NIST AI 100-2e2023. Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations. DOI: 10.6028/NIST.AI.100-2e2023.
14. Bai T, et al. Adversarial Training: A Survey. IJCAI. 2021. DOI: 10.24963/ijcai.2021/591.
15. NIST AI RMF 1.0. DOI: 10.6028/NIST.AI.100-1.
16. ISO/IEC 42001:2023. Artificial intelligence management system.
17. Brakenhoff TB, et al. The Measurement Error Elephant in the Room. Epidemiologic Reviews. DOI: 10.1093/epirev/mxab011.
18. STRATOS measurement error guidance. DOI: 10.1002/sim.8532.
19. Brakenhoff TB, et al. Systematic review on measurement error. Journal of Clinical Epidemiology. DOI: 10.1016/j.jclinepi.2018.02.023.
20. METRIC framework. npj Digital Medicine. 2024. DOI: 10.1038/s41746-024-01196-4.
21. ISO 8000-8:2015. Data quality: information and data quality concepts.
22. ISO 8000-1:2022. Data quality — Part 1: Overview.
23. GDPR Article 5. EUR-Lex.
24. ISO/IEC 38505-1:2017. Governance of data.
25. DAMA-DMBOK. Data Management Body of Knowledge.
26. NIST Privacy Framework 1.0.
27. Dwork C, Roth A. The Algorithmic Foundations of Differential Privacy. Foundations and Trends in Theoretical Computer Science. DOI: 10.1561/0400000042.
28. ISO/IEC 27001:2022. Information security management systems.
29. OWASP Machine Learning Security Top 10.
30. Coveney PV, Groen D, Hoekstra AG. Reproducibility in computational science. DOI: 10.1098/rsta.2020.0409.
31. Lynch E, et al. Computational reproducibility. DOI: 10.1098/rsta.2020.0069.
32. The five pillars of computational reproducibility. PMC10591307.
33. Wilkinson MD, et al. The FAIR Guiding Principles for scientific data management and stewardship. Scientific Data. 2016. DOI: 10.1038/sdata.2016.18.
34. Peng RD. Reproducible Research in Computational Science. Science. DOI: 10.1126/science.aah6168.

## Verification Notes

The research package distinguishes primary and secondary evidence, peer-reviewed work, benchmarks, technical resources and preprints. DOI and canonical-URL verification should be repeated before a source is promoted from bibliographic evidence to a normative implementation dependency. Lower-authority or duplicate sources should not be allowed to inflate evidence independence.

**Document Status:** Complete  
**Last Updated:** September 13, 2026  
**Next Steps:** Validate methods on healthcare surveillance datasets and implement a prototype detection pipeline.