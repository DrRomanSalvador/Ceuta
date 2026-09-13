# CeutIA-Serpiente — Package 2: Causality and temporal reasoning

**Research date:** 13 September 2026  
**Scope:** authoritative primary papers, methodological reviews, books/standards, and official sources relevant to an epistemic-analytical system for evidence management, causal inference, regime detection, and anomaly detection.

## 0. Verification and interpretation policy

Identifiers below were checked against publisher pages, journal pages, PubMed/PMC records, institutional repositories, or official project pages. Where a source is a book without a journal DOI, the publisher or library URL is given. Search-result-only, informal, predatory, or unverifiable references were excluded. “Independence” means independence of evidence from the other listed items—not that authors have no institutional relationships.

A central design distinction is essential: a DAG represents contemporaneous causal structure under acyclicity; feedback can be represented by explicit time indices (unrolling the system into a DAG), by dynamic SCMs, or by cyclic SCMs with additional solvability assumptions. A detected temporal dependency is not automatically an intervention effect.

## 1. Causal inference in complex systems

### 1.1 Pearl, *Causality: Models, Reasoning, and Inference*
- **Authors/year/type:** Judea Pearl; 2009, 2nd ed.; authoritative monograph.
- **Verified identifier:** https://doi.org/10.1017/CBO9780511803161
- **Key methods/findings:** Formalizes structural causal models, causal DAGs, d-separation, interventions, counterfactuals, back-door/front-door criteria, and do-calculus. It separates association, intervention, and counterfactual reasoning.
- **CeutIA application:** Use as the semantic and mathematical contract for causal claims. Require every causal claim to specify graph, intervention, estimand, assumptions, observed/latent variables, and whether the output is associational, interventional, or counterfactual.
- **Limitations:** Identification depends on a sufficiently correct causal graph and assumptions such as consistency, positivity, and appropriate treatment of confounding. Standard DAGs do not directly encode instantaneous feedback cycles.
- **Independence:** Foundational source; independent of the later reviews and cyclic-SCM papers below.

### 1.2 Yuan et al., “Emergence and Causality in Complex Systems: A Survey of Causal Emergence and Related Quantitative Studies”
- **Authors/year/type:** Bing Yuan, Jiang Zhang, Aobo Lyu, Jiayun Wu, Zhipeng Wang, Mingzhe Yang, Kaiwei Liu, Muyun Mou, Peng Cui; 2024; survey/review, *Entropy* 26(2):108.
- **Verified DOI:** https://doi.org/10.3390/e26020108
- **Key methods/findings:** Reviews causal emergence, effective information, computational mechanics, Granger-style approaches, partial-information decomposition, causal representation learning, and causal analysis across scales. It explicitly distinguishes Markovian dynamics—with temporal circular interactions—from standard DAG/SCM representations and describes time expansion as a way to remove cycles in the graph.
- **CeutIA application:** Supports a multi-scale layer: micro-level evidence, meso-level mechanisms, and macro-level regimes. A regime detector should not infer macro causation merely from predictive compression or effective information; it should retain the aggregation/coarse-graining choice and test sensitivity.
- **Limitations:** Broad survey rather than a single validated estimator; causal-emergence measures can depend on coarse-graining, data-processing choices, and computationally difficult optimization. Some cross-level causal interpretations remain debated.
- **Independence:** Independent review synthesis; overlaps conceptually with Pearl but has different authorship and emphasis.

### 1.3 Bühlmann et al., “Causal Structure Learning and Inference: A Selective Review”
- **Authors/year/type:** Peter Bühlmann and colleagues; 2014-era review manuscript; methodological review.
- **Verified URL:** https://stat.ethz.ch/Manuscripts/buhlmann/causal-review-2013v3.pdf
- **Key methods/findings:** Reviews structural-equation models, constraint-based and score-based causal discovery, Markov/faithfulness assumptions, do-calculus, and back-door identification. It stresses that causal discovery generally returns an equivalence class rather than a unique graph unless additional assumptions or interventions are available.
- **CeutIA application:** Implement graph outputs as sets of compatible models, not a single “truth” by default. Store conditional-independence tests, assumptions, equivalence class, confidence, and sensitivity to hidden confounding.
- **Limitations:** Selective rather than systematic; much of the theory presumes acyclic graphs and reliable conditional-independence testing. Finite samples, measurement error, selection bias, and nonstationarity can invalidate conclusions.
- **Independence:** Independent review, though it covers Pearl and Spirtes traditions.

### 1.4 Spirtes, Glymour & Scheines, *Causation, Prediction, and Search*
- **Authors/year/type:** Peter Spirtes, Clark Glymour, Richard Scheines; 2nd ed. 2000/2001; monograph.
- **Verified URL:** MIT Press: https://direct.mit.edu/books/monograph/2057/Causation-Prediction-and-Search
- **Verified book DOI/record:** https://doi.org/10.1007/978-1-4612-2748-9 (Springer record for the earlier edition; do not confuse it with the MIT Press 2nd-edition ISBN 0-262-19440-6).
- **Key methods/findings:** Develops constraint-based causal discovery, including graphical Markov properties, conditional independence, equivalence classes, and algorithms such as PC/related approaches. The core message is that observational data plus assumptions constrain causal structures but frequently do not identify one unique DAG.
- **CeutIA application:** Use as the basis for an “alternative graph set” module and for explicit rival causal structures. CeutIA can report compelled edges, uncertain edges, separating sets, and assumptions rather than overclaiming directionality.
- **Limitations:** Classical results rely on acyclicity, causal sufficiency or explicit latent-variable extensions, faithfulness, and accurate independence tests. High-dimensional and dependent time-series data require specialized methods.
- **Independence:** Foundational but methodologically distinct from Pearl’s intervention calculus.

## 2. Causality with feedback loops

### 2.1 Bongers, Forré, Peters & Mooij, “Foundations of Structural Causal Models with Cycles and Latent Variables”
- **Authors/year/type:** Stephan Bongers, Patrick Forré, Jonas Peters, Joris M. Mooij; 2021; peer-reviewed theoretical paper, *Annals of Statistics* 49(5):2885–2915.
- **Verified DOI:** https://doi.org/10.1214/21-AOS2064
- **Key methods/findings:** Generalizes SCMs to cycles and latent variables. It shows that cyclic SCMs may lack solutions, have non-unique observational/interventional/counterfactual distributions, fail to satisfy ordinary Markov properties, and require solvability conditions. It introduces “simple SCMs” preserving useful properties in cyclic settings.
- **CeutIA application:** A feedback-aware causal engine should attach a solvability/uniqueness certificate to every cyclic model. If no certificate exists, return “non-identifiable or non-unique” rather than a point estimate. Separate equilibrium causality from dynamic causal effects.
- **Limitations:** The theory does not make arbitrary cyclic systems automatically identifiable; assumptions can be mathematically demanding and difficult to verify empirically. Practical estimation remains more difficult than DAG-based estimation.
- **Independence:** Primary theoretical source; independent of the applied time-series review by Runge et al.

### 2.2 Boeken & Mooij, “Dynamic Structural Causal Models”
- **Authors/year/type:** Philip Boeken, Joris M. Mooij; 2024 workshop paper/preprint, revised 2026; methodological paper.
- **Verified identifier:** https://doi.org/10.48550/arXiv.2406.01161 and https://arxiv.org/abs/2406.01161
- **Key methods/findings:** Defines DSCMs whose endogenous variables are functions of time, allowing cyclic temporal structure and latent confounding. It provides a framework for causal reasoning over stochastic processes rather than isolated cross-sectional variables.
- **CeutIA application:** Use DSCMs as the native representation for longitudinal evidence: variable trajectories, lagged mechanisms, interventions over time, and time-varying confounders. A graph view should expose both within-time and across-time edges.
- **Limitations:** The cited version is a workshop/preprint record rather than a mature journal standard; assumptions and estimators should be independently validated before production use. Continuous-time, irregular sampling, measurement error, and missingness require extra modeling.
- **Independence:** Independent primary contribution, but closely related to the cyclic-SCM foundations paper.

### 2.3 Runge et al., “Inferring causation from time series in Earth system sciences”
- **Authors/year/type:** Jakob Runge, Sebastian Bathiany, Erik Bollt, Gustau Camps-Valls, Dim Coumou, Ethan Deyle, Clark Glymour, Marlene Kretschmer, Martin D. Mahecha, Jordi Muñoz-Marí, Egbert H. van Nes, Jonas Peters, R. Quax, Markus Reichstein, Marten Scheffer, Bernhard Schölkopf, Peter Spirtes, Jan Sun, Kun Zhang, Jürgen Zscheischler; 2019; peer-reviewed methodological review/tutorial, *Nature Communications* 10:2553.
- **Verified DOI:** https://doi.org/10.1038/s41467-019-10105-3
- **Key methods/findings:** Reviews time-series causal discovery for complex spatiotemporal systems and methods that distinguish direct from indirect links and common drivers. It explains why ordinary correlation is ambiguous and discusses temporal conditioning, lag structure, nonlinear methods, and causal networks.
- **CeutIA application:** Useful for the temporal causal-discovery pipeline: lagged candidate generation, conditioning on drivers, spatial/temporal controls, and comparison of multiple algorithms. It also supports regime-change monitoring when causal links—not merely correlations—change over time.
- **Limitations:** Many methods require stationarity, adequate sampling, correct lag windows, and controlled confounding. Time-series causal discovery is vulnerable to autocorrelation, common trends, synchrony, finite samples, and unmeasured drivers.
- **Independence:** Independent multi-author review; not an official standard.

### 2.4 Drton, Fox & Wang, “Computation of Maximum Likelihood Estimates in Cyclic Structural Equation Models”
- **Authors/year/type:** Mathias Drton, Christopher Fox, Y. Samuel Wang; 2019; peer-reviewed statistical paper, *Annals of Statistics* 47(2):663–690.
- **Verified DOI:** https://doi.org/10.1214/17-AOS1602
- **Key methods/findings:** Studies likelihood-based estimation for cyclic structural equation models and computational issues arising from nonrecursive systems.
- **CeutIA application:** Provides a route for estimating parameters in feedback models where ordinary recursive regression is invalid. Candidate models can be fit and compared using likelihood diagnostics, while retaining explicit stability and identification checks.
- **Limitations:** Parametric assumptions and model specification matter; likelihood estimation does not by itself establish causal direction or resolve hidden confounding. Numerical convergence is not proof of a valid causal model.
- **Independence:** Independent estimation-focused paper, complementary to the foundational theory.

## 3. Rival hypotheses and falsification

### 3.1 Rajtmajer, Errington & Hillary, “How failure to falsify in high-volume science contributes to the replication crisis”
- **Authors/year/type:** Sarah M. Rajtmajer, Timothy M. Errington, Frank G. Hillary; 2022; peer-reviewed methodological/critical paper, *eLife* 11:e78830.
- **Verified DOI:** https://doi.org/10.7554/eLife.78830
- **Key methods/findings:** Argues for strong, specific, risky hypotheses with pre-specified observations that would challenge them. Uses competing traumatic-brain-injury hypotheses to show how a literature can preserve incompatible explanations when studies only seek supportive results. It explicitly notes that falsification is provisional, not logically absolute.
- **CeutIA application:** Represent each claim as a hypothesis object with: prediction, rival hypotheses, discriminating observation, required data, pre-registration/provenance, falsification threshold, and residual uncertainty. Penalize claims that explain every possible outcome.
- **Limitations:** It is a methodological argument and illustrative case, not a universal quantitative test of falsifiability. Real-world refutation can be confounded by measurement error, auxiliary assumptions, low power, and model misspecification.
- **Independence:** Independent of the statistical multiple-testing sources; conceptually aligned with Popperian practice but modernized through replication and transparency.

### 3.2 Benjamini & Hochberg, “Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing”
- **Authors/year/type:** Yoav Benjamini, Yosef Hochberg; 1995; foundational peer-reviewed statistical paper, *JRSS Series B* 57(1):289–300.
- **Verified DOI:** https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
- **Key methods/findings:** Introduces the BH procedure controlling the expected false discovery rate under independence and gives conditions/extensions for dependence. FDR is often more suitable than family-wise error control when thousands of hypotheses are tested.
- **CeutIA application:** Use FDR control for large-scale anomaly, biomarker, literature-signal, and candidate-causal-edge screening. Report adjusted q-values, the tested family, dependence assumptions, and whether hypotheses were pre-specified or discovered post hoc.
- **Limitations:** FDR control is not a guarantee that every selected claim is true; dependence structure, adaptive search, sequential monitoring, and selection of the testing family affect validity. It does not solve confounding or causal identification.
- **Independence:** Independent foundational statistics paper.

### 3.3 Yekutieli & Benjamini, “The Control of the False Discovery Rate in Multiple Testing under Dependency”
- **Authors/year/type:** Yoav Benjamini, Daniel Yekutieli; 2001; peer-reviewed theoretical paper, *Annals of Statistics* 29(4):1165–1188.
- **Verified DOI:** https://doi.org/10.1214/aos/1013699998
- **Key methods/findings:** Extends FDR control to positive regression dependence and offers a conservative modification for more general dependency. This is important because evidence streams and time-series anomaly tests are rarely independent.
- **CeutIA application:** Choose BH only when its dependence assumptions are defensible; otherwise use conservative or resampling-based procedures. For correlated evidence, cluster hypotheses by mechanism and report the dependency strategy.
- **Limitations:** Procedures can be conservative and reduce power; arbitrary, unknown, or adaptive dependence remains challenging. Multiple looks at data and model selection need additional control.
- **Independence:** Independent extension of the BH framework.

### 3.4 G’Sell, Wager, Chouldechova & Tibshirani, “Sequential Selection Procedures and False Discovery Rate Control”
- **Authors/year/type:** Max G’Sell, Stefan Wager, Alexandra Chouldechova, Robert Tibshirani; 2016; peer-reviewed statistical paper, *Journal of the Royal Statistical Society: Series B* 78(2):423–444.
- **Verified DOI:** https://doi.org/10.1111/rssb.12126
- **Key methods/findings:** Develops procedures for controlling false discoveries during sequential testing/selection, including ordered hypotheses and accumulation-style ideas. This is relevant when a system continuously evaluates evidence or anomalies.
- **CeutIA application:** For streaming evidence, do not repeatedly apply a one-shot p-value threshold. Use an explicitly sequential error-control layer, log stopping rules, and distinguish exploratory alerts from confirmed findings.
- **Limitations:** Validity depends on the sequential structure and assumptions; online procedures may sacrifice power. The framework is not a substitute for causal design or replication.
- **Independence:** Independent from BH/BY in authorship and method, while extending the same error-control objective.

### 3.5 Popperian falsification: operational interpretation
- **Primary source used here:** Rajtmajer et al. 2022 above; direct source for the practical modern treatment. The system should not encode “falsified” as metaphysical disproof.
- **Operational rule for CeutIA:** classify claims as supported, challenged, unresolved, or refuted-under-specified-conditions. A “refuted” label must identify the failed prediction, measurement validity, auxiliary assumptions, replication status, and whether an alternative model explains the observation better.
- **Limitations:** No empirical test isolates a theory from all auxiliary assumptions. Failed predictions may reflect implementation, measurement, sampling, or regime mismatch.
- **Independence:** This is a design synthesis, not a separate source.

## 4. Dynamic and temporal models

### 4.1 Durbin & Koopman, *Time Series Analysis by State Space Methods*
- **Authors/year/type:** James Durbin, Siem Jan Koopman; 2012, 2nd ed.; authoritative monograph.
- **Verified publisher/library record:** Stanford Libraries: https://searchworks.stanford.edu/view/9438388
- **Key methods/findings:** Provides state-space representations, Kalman filtering and smoothing, likelihood-based estimation, missing observations, structural time-series models, and extensions to non-Gaussian observations. A state-space model separates latent state dynamics from the observation process.
- **CeutIA application:** Use latent states for regime detection, denoising, missing-data handling, sensor fusion, and time-varying parameters. Store filtered versus smoothed states separately because smoothing can use future observations and is unsuitable for real-time alerting.
- **Limitations:** Classical linear-Gaussian models can miss nonlinear dynamics, heavy tails, abrupt transitions, and nonstationarity; complex models can be weakly identified. Filtering/smoothing outputs depend on transition and observation specifications.
- **Independence:** Independent time-series monograph; complementary to causal-model sources.

### 4.2 Durbin & Koopman, “Time Series Analysis of Non-Gaussian Observations Based on State Space Models from Both Classical and Bayesian Perspectives”
- **Authors/year/type:** James Durbin, Siem Jan Koopman; 2000; peer-reviewed methodological paper, *JRSS Series B* 62(1):3–56.
- **Verified DOI:** https://doi.org/10.1111/1467-9868.00218
- **Key methods/findings:** Extends state-space analysis beyond Gaussian observations using simulation, importance sampling, and Bayesian/classical inference, supporting count, binary, and other non-Gaussian observations.
- **CeutIA application:** Important for health, event, safety, and literature data where observations are counts, binary events, rare alerts, or skewed measurements. Keep the observation distribution explicit instead of forcing Gaussian residuals.
- **Limitations:** Estimation can be computationally expensive and sensitive to approximation quality; nonlinear/non-Gaussian models may have weakly identified states. Causal interpretation still requires a causal design.
- **Independence:** Independent methodological paper by the same authors as the monograph; treat it as a technical companion rather than independent empirical replication.

### 4.3 Koopman & Durbin, “Filtering and Smoothing of State Vector for Diffuse State-Space Models”
- **Authors/year/type:** Siem Jan Koopman, James Durbin; 2003; peer-reviewed methods paper, *Journal of Time Series Analysis* 24:85–98.
- **Verified DOI:** https://doi.org/10.1111/1467-9892.00294
- **Key methods/findings:** Gives exact recursions for filtering and smoothing in multivariate linear Gaussian state-space models with diffuse initial conditions.
- **CeutIA application:** Supports robust initialization when latent levels/trends are not known. It is useful for separating baseline drift from anomalies and for avoiding spurious “regime changes” caused by arbitrary initial-state assumptions.
- **Limitations:** Focuses on linear Gaussian models and diffuse initialization; nonlinear, regime-switching, and irregular-time applications require extensions.
- **Independence:** Technical companion, not independent of Durbin–Koopman methodology.

### 4.4 Runge et al. 2019 temporal-causality review
- **Source:** See §2.3; https://doi.org/10.1038/s41467-019-10105-3
- **Relevance:** It connects temporal lags, direct/indirect links, common drivers, and nonlinear/spatiotemporal causal discovery. It should be paired with state-space modeling: state-space models describe latent dynamics; causal time-series methods address directional mechanism claims.
- **Limitations:** Predictive lag structure alone is insufficient for intervention claims; assumptions and stationarity must be audited.
- **Independence:** Independent review, but reused because it is directly relevant to both feedback and temporal causality.

### 4.5 PRISMA 2020 Statement
- **Authors/year/type:** Page, McKenzie, Bossuyt, Boutron, Hoffmann, Mulrow, Shamseer, Tetzlaff, Akl, Brennan, Chou, Glanville, Grimshaw, Hróbjartsson, Lalu, Li, Loder, Mayo-Wilson, McDonald, McGuinness, Stewart, Thomas, Tricco, Welch, Whiting, Moher; 2021; reporting guideline/standard for systematic reviews.
- **Verified DOI:** https://doi.org/10.1136/bmj.n71
- **Official URL:** https://www.prisma-statement.org/prisma-2020-statement
- **Key methods/findings:** Provides a 27-item checklist, abstract checklist, and flow diagrams for transparent reporting of search, selection, synthesis, certainty, conflicts, and data/code availability.
- **CeutIA application:** Use as the evidence-ingestion protocol: record search strings, databases, dates, deduplication, inclusion/exclusion, study identifiers, extraction fields, risk of bias, synthesis decisions, and updates. It directly reduces provenance gaps in the evidence graph.
- **Limitations:** PRISMA is a reporting guideline, not proof of methodological quality and not a causal-inference standard. It does not replace risk-of-bias tools, GRADE, or domain-specific methods.
- **Independence:** Official reporting guideline and independent from the causal-model literature; highly relevant to CeutIA’s evidence-management layer.

## 5. Cross-topic architecture for CeutIA-Serpiente

### 5.1 Recommended causal object
Each claim should be represented as:
1. **Target:** outcome, population, time window, and unit of analysis.
2. **Hypothesis:** directional mechanism and expected magnitude/range.
3. **Rivals:** mutually distinguishable alternative mechanisms, null, reverse-causality, confounding, selection, measurement-error, and regime-specific explanations.
4. **Graph/model:** DAG, ADMG, dynamic SCM, cyclic SCM, state-space model, or a declared hybrid.
5. **Assumptions:** consistency, positivity, no/known hidden confounding, stationarity or transition law, sampling mechanism, measurement model, and stability/solvability.
6. **Evidence:** source identifiers, extraction locations, population, design, effect estimate, uncertainty, and provenance.
7. **Decision status:** supported, challenged, unresolved, or refuted under specified conditions.

### 5.2 Regime detection
Use a two-layer design:
- **State layer:** latent-state/state-space or switching model estimates hidden regimes, trends, and observation noise.
- **Causal layer:** dynamic/cyclic causal model tests whether mechanisms, lagged effects, or intervention responses differ by regime.

A regime change should require more than a residual spike: evidence can include posterior/state probability, parameter instability, predictive degradation, causal-edge instability, and replication across independent data streams.

### 5.3 Feedback protocol
1. Start with a time-unrolled graph where possible.
2. Test lagged directionality and common drivers.
3. If contemporaneous cycles are required, use a cyclic SCM and report solvability/uniqueness conditions.
4. Distinguish equilibrium effects from transient effects.
5. Run interventions or natural experiments where feasible.
6. Preserve unresolved cyclic alternatives rather than collapsing them into a DAG.

### 5.4 Falsification and multiplicity protocol
- Pre-register or timestamp predictions before outcome inspection where possible.
- Keep exploratory and confirmatory analyses separate.
- Test rival hypotheses against the same data and outcome definitions.
- Control FDR for large candidate sets and use sequential control for streaming alerts.
- Require replication or independent evidence before promoting an anomaly to a causal claim.
- Record negative evidence and failed predictions as first-class data.

## 6. Limitations of this package

This package is a high-value methodological foundation, not a complete systematic review of every causal and temporal method. Search results contain heterogeneous source types, and several central methods are books or methodological papers rather than clinical systematic reviews. The sources do not establish that any specific CeutIA implementation will identify causal effects: validity remains dependent on domain knowledge, data quality, model assumptions, sampling, measurement, and external validation. Preprints/workshop material—especially DSCMs—should be version-pinned and rechecked before being treated as settled standards.

## 7. Verified source index

1. Pearl 2009: https://doi.org/10.1017/CBO9780511803161
2. Yuan et al. 2024: https://doi.org/10.3390/e26020108
3. Bühlmann et al. review: https://stat.ethz.ch/Manuscripts/buhlmann/causal-review-2013v3.pdf
4. Spirtes et al.: https://direct.mit.edu/books/monograph/2057/Causation-Prediction-and-Search
5. Bongers et al. 2021: https://doi.org/10.1214/21-AOS2064
6. Boeken & Mooij: https://doi.org/10.48550/arXiv.2406.01161
7. Runge et al. 2019: https://doi.org/10.1038/s41467-019-10105-3
8. Drton et al. 2019: https://doi.org/10.1214/17-AOS1602
9. Rajtmajer et al. 2022: https://doi.org/10.7554/eLife.78830
10. Benjamini & Hochberg 1995: https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
11. Benjamini & Yekutieli 2001: https://doi.org/10.1214/aos/1013699998
12. G’Sell et al. 2016: https://doi.org/10.1111/rssb.12126
13. Durbin & Koopman 2012 record: https://searchworks.stanford.edu/view/9438388
14. Durbin & Koopman 2000: https://doi.org/10.1111/1467-9868.00218
15. Koopman & Durbin 2003: https://doi.org/10.1111/1467-9892.00294
16. PRISMA 2020: https://doi.org/10.1136/bmj.n71
