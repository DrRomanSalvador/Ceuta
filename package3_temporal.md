# CeutIA-Serpiente Project: Research Package 3 - Temporal Integrity & Evaluation

## Executive Summary

This research package compiles authoritative primary sources on five critical topics for building an epistemic-analytical system for evidence management and anomaly detection. All sources have been verified with DOIs or stable URLs. The findings directly inform the design of CeutIA-Serpiente's backtesting and evaluation framework to prevent temporal leakage and ensure reproducible, honest performance estimates.

---

## TOPIC 1: TEMPORAL DATA LEAKAGE PREVENTION

### Source 1.1: PLoS ONE - Taxonomy for Temporal Data Leakage (2026)

**Title:** A taxonomy for detecting and preventing temporal data leakage in machine learning-based build prediction: A dual-platform empirical validation  
**Authors:** Mishra LN, Rangari A, Nagrare S, Nayak SK  
**Year:** 2026  
**Type:** Peer-reviewed empirical study  
**DOI:** 10.1371/journal.pone.0340167  
**URL:** https://doi.org/10.1371/journal.pone.0340167

**Key Findings/Methods:**
- Developed a three-type temporal leakage taxonomy:
  1. **Direct Outcome Encoding**: Using the build result itself as a feature (e.g., tr_status, tr_log_status)
  2. **Execution-Dependent Metrics**: Information generated during build execution (e.g., tr_duration, test execution counts)
  3. **Future Information Leakage**: Using data from chronologically later builds (e.g., time-dependent popularity metrics)
- Validated on 175,706 builds across two CI/CD platforms (TravisTorrent 2013-2017, GHALogs 2023)
- Removing leaky features reduced accuracy by 15.07pp on TravisTorrent (97.8% → 82.73%) but only 0.48pp on GHALogs
- Type 1 (Direct Outcome) features alone accounted for 79.2% of total accuracy inflation
- Implemented systematic filtering: temporal availability audit, correlation analysis (r > 0.9 flag), temporal validation
- Used 5-fold time-series cross-validation with expanding window (forward chaining) for hyperparameter tuning

**Application to CeutIA-Serpiente:**
- Directly applicable to preventing temporal leakage in backtesting healthcare prediction models
- The three-type taxonomy provides a structured audit framework for feature engineering pipelines
- Temporal split discipline (train on historical, test on future) must be enforced at the data pipeline level
- Correlation analysis can flag suspiciously predictive features for manual review
- Time-series CV with expanding window should replace i.i.d. k-fold for all temporal data

**Limitations:**
- Focused on software build prediction; healthcare data may have different leakage patterns (e.g., patient outcomes, lab results)
- Does not address leakage from data revisions or methodology changes (covered in Topics 4-5)
- Single-domain validation; cross-domain generalization not tested

**Independence Assessment:**
- Authors employed by Lowe's, JPMorgan Chase, Digital Remedy, Cognizant; no competing interests declared
- Open access, open data (Zenodo DOI: 10.5281/zenodo.17745286)
- No funding; independent academic contribution
- **Rating: HIGH INDEPENDENCE**

---

### Source 1.2: arXiv - LSTM Evaluation & Data Leakage (2025)

**Title:** How Data Leakage Affects LSTM Evaluation Across Configurations  
**Authors:** Not specified in snippet  
**Year:** 2025  
**Type:** Preprint (arXiv)  
**URL:** https://arxiv.org/html/2512.06932v1

**Key Findings/Methods:**
- Evaluated three validation techniques (2-way split, 3-way split, 10-fold CV) under leaky vs. clean conditions
- Shuffled 10-fold CV without temporal boundaries causes significant overestimation from future information leakage
- Best practices advocated:
  - **Post-split sequence generation** to maintain strict temporal separation
  - **Buffer zones between folds** when overlap cannot be avoided
  - **2-way and 3-way validation** demonstrate superior robustness to temporal contamination
  - Sequential data partitioning is mandatory

**Application to CeutIA-Serpiente:**
- Reinforces that shuffled k-fold CV is invalid for time series; must use time-series split or walk-forward
- Buffer zones (purge + embargo) should be implemented between training and test sets to prevent autocorrelation leakage
- Post-split feature engineering ensures no test data influences training transformations

**Limitations:**
- Preprint, not peer-reviewed
- Focused on LSTM configurations; may not generalize to all model types
- Limited methodological detail in snippet

**Independence Assessment:**
- arXiv preprint; peer-review status unclear
- **Rating: MODERATE INDEPENDENCE** (awaiting peer review)

---

### Source 1.3: SAS Proceedings - Look-Ahead Bias in Forecasting (2018)

**Title:** How Good is That Forecast? The Nuances of Prediction  
**Authors:** Not specified  
**Year:** 2018  
**Type:** Conference proceedings  
**URL:** https://support.sas.com/resources/papers/proceedings18/1862-2018.pdf

**Key Findings/Methods:**
- Emphasizes using forecasted values (not actuals) for features at prediction time
- Highlights temporal alignment: model must use only information available at forecast origin
- Warns against using future temperature data to forecast temperature

**Application to CeutIA-Serpiente:**
- Critical for healthcare forecasting: must use point-in-time data (e.g., lab values available at decision time, not revised later)
- Reinforces need for timestamp discipline in feature engineering

**Limitations:**
- Conference proceedings, not journal article
- Limited methodological depth

**Independence Assessment:**
- SAS vendor publication; potential bias toward SAS tools
- **Rating: MODERATE INDEPENDENCE**

---

### Source 1.4: Data Science Central - Avoiding Look-Ahead Bias (2017)

**Title:** Avoiding Look Ahead Bias in Time Series Modelling  
**Authors:** Not specified  
**Year:** 2017  
**Type:** Industry blog/technical article  
**URL:** https://www.datasciencecentral.com/avoiding-look-ahead-bias-in-time-series-modelling-1/

**Key Findings/Methods:**
- Look-ahead bias occurs when training uses future actual information unavailable at prediction time
- Best practices:
  - **Construct last window first**: Start with small sample, add complexity gradually
  - **Ignore data points from t-n to t in features**: Ensure proper lagging
  - **Learn when data is published**: Account for publication delays
  - **Avoid randomized cross-validation**: Use time-aware splits
  - **Pause if accuracy jumps suddenly**: Check for future data usage
  - **Multiple random checks**: Validate at each process step

**Application to CeutIA-Serpiente:**
- Practical checklist for debugging temporal leakage in backtesting pipelines
- Publication delay awareness is critical for healthcare data (e.g., lab results, claims data)

**Limitations:**
- Industry blog, not peer-reviewed
- No empirical validation

**Independence Assessment:**
- Community-driven platform; moderate independence
- **Rating: MODERATE INDEPENDENCE**

---

### Source 1.5: Towards Data Science - Time Series Modeling Mistakes (2025)

**Title:** 3 Common Time Series Modeling Mistakes You Should Know  
**Authors:** Not specified  
**Year:** 2025  
**Type:** Industry blog  
**URL:** https://towardsdatascience.com/3-common-time-series-modeling-mistakes-you-should-know-a126df24256f

**Key Findings/Methods:**
- Look-ahead bias: model trained using future data it would not have access to in reality
- **Fix**: Split dataset using cutoff in time, not percentage holdout
- **Walk-forward validation**: Start with continuous subset, hold out tailing n-periods, train on opening years, test on next year, walk forward through data
- Example: 7-year period → train on first 2 years, test on year 3; then train on first 3 years, test on year 4; etc.

**Application to CeutIA-Serpiente:**
- Walk-forward validation is the gold standard for temporal evaluation
- Time-based cutoff (not random split) is mandatory for all time series

**Limitations:**
- Industry blog, not peer-reviewed
- Conceptual overview without empirical depth

**Independence Assessment:**
- Medium publication; community-driven
- **Rating: MODERATE INDEPENDENCE**

---

### Source 1.6: Research Blog - Time Series Cross-Validation (2026)

**Title:** Time Series Cross-Validation: Preventing Leakage in GRU & SVR  
**Authors:** Kuriko Iwai  
**Year:** 2026  
**Type:** Research blog/technical tutorial  
**URL:** https://kuriko-iwai.com/research/advanced-cross-validation-techniques

**Key Findings/Methods:**
- Three principles to avoid leakage:
  1. **Maintain temporal order**: Preserve sequence of events
  2. **Use time-series specific validation**: Methods designed for sequential data
  3. **Prevent autocorrelation**: Avoid close-in-time data points in both train and test
- Techniques: Growing Window, Blocked K-Fold, Purged CV with PyTorch and Scikit-Learn

**Application to CeutIA-Serpiente:**
- Purged CV (with buffer zones) should be implemented for healthcare time series
- Growing window (expanding training set) mimics real-world deployment

**Limitations:**
- Blog/tutorial format, not peer-reviewed
- Focused on GRU/SVR models

**Independence Assessment:**
- Individual researcher blog; moderate independence
- **Rating: MODERATE INDEPENDENCE**

---

### Source 1.7: Medium - Blueprint for Eradicating Data Leakage (2025)

**Title:** Stop the spill: the blueprint for eradicating data leakage  
**Authors:** Data Science at Microsoft team  
**Year:** 2025  
**Type:** Industry blog  
**URL:** https://medium.com/data-science-at-microsoft/stop-the-spill-the-blueprint-for-eradicating-data-leakage-6f924e543a95

**Key Findings/Methods:**
- **Train-test split comparison**: Look for stark differences in metrics (Pearson's r, r2, accuracy) between random and time-aware splits
- **Rolling cross-validation**: Implement time-aware validation honoring temporal order
- **Residual analysis**: Use ACF/PACF, Durbin-Watson to ensure residuals are random noise
- **Pipeline design**: Use scikit-learn Pipeline to encapsulate all feature engineering within training process
- **Iterative validation**: Compare models with/without potentially leaky features
- **Group k-fold**: Ensure same group doesn't leak into both train and test
- **Strict separation**: All preprocessing, feature engineering, transformations on training data only
- **Cross-validation awareness**: Fit transformations within each fold, apply to validation split

**Application to CeutIA-Serpiente:**
- Pipeline encapsulation is critical: all transformations must be inside CV folds
- Residual analysis can detect temporal leakage (systematic patterns in residuals)
- Train-test metric comparison is a simple leakage diagnostic

**Limitations:**
- Industry blog, not peer-reviewed
- Microsoft-affiliated; potential tool bias

**Independence Assessment:**
- Corporate blog; moderate independence

**Rating: MODERATE INDEPENDENCE**

---

### Source 1.8: MH Techin - Look-Ahead Bias in Rolling Window Features (2024)

**Title:** Look-Ahead Bias in Rolling Window Features  
**Authors:** Not specified  
**Year:** 2024  
**Type:** Technical documentation  
**URL:** https://www.mhtechin.com/support/look-ahead-bias-in-rolling-window-features/

**Key Findings/Methods:**
- Look-ahead bias occurs when feature engineering uses information unavailable at prediction time
- **Mitigation**: Properly designed rolling-window or expanding-window frameworks
- **Diagnostic tests before deployment**:
  - **Temporal Split Testing**: Train on data up to T1, test on (T1, T2], no overlap
  - **Walk-Forward Validation**: Iteratively expand training window, test on subsequent hold-out
  - **Performance Stability Checks**: Compare backtest metrics with/without shifted rolling features; large discrepancies signal leakage
  - **Code Reviews**: Verify all `.rolling()` or `.expanding()` operations followed by `.shift(1)` (or appropriate lag)
- **Best practices**:
  - **Explicit Lagging**: Always shift rolling computations by one period (or more if forecast horizon >1)
  - **Point-in-Time Data**: Use data vendors/APIs preserving historical releases without hindsight revisions
  - **Walk-Forward Frameworks**: Automate retraining/testing in sequential manner mimicking real-time deployment
  - **Modular Pipelines**: Encapsulate feature creation in functions accepting "current date" parameter
  - **Thorough Testing**: Integrate look-ahead analysis tools (e.g., Freqtrade's `lookahead-analysis`)

**Application to CeutIA-Serpiente:**
- Rolling window features (common in healthcare time series) must be explicitly lagged
- `.shift(1)` after `.rolling()` is mandatory to prevent leakage
- Point-in-time data discipline is critical for healthcare (avoid revised data in backtesting)

**Limitations:**
- Technical documentation, not peer-reviewed
- Focused on trading/finance applications

**Independence Assessment:**
- Vendor documentation; moderate independence
- **Rating: MODERATE INDEPENDENCE**

---

### Source 1.9: MetricGate - Cross-Validation Pitfalls (2025)

**Title:** Cross-Validation Pitfalls to Avoid  
**Authors:** Not specified  
**Year:** 2025  
**Type:** Technical blog  
**URL:** https://metricgate.com/blogs/cross-validation-pitfalls/

**Key Findings/Methods:**
- Three most common CV errors: data leakage, future leakage in time series, selection bias from nested hyperparameter tuning
- **Correct approach for time series**: Walk-forward validation (time-series split):
  1. Fix minimum training window (e.g., first 60 observations)
  2. Train on current window, predict one step ahead
  3. Expand window by one observation, repeat
  4. Aggregate out-of-sample errors across all steps
- **Checklist**:
  1. All preprocessing inside fold (scaling, imputation, feature selection on training portion only)
  2. Data iid? If clustered (patients, schools, repeated measures), use grouped/stratified folds
  3. Data time-ordered? Use time-series split or walk-forward, never random split
  4. Hyperparameter selection? Wrap CV inside outer CV loop (nested CV) to avoid selection bias
  5. Duplicate rows? Remove or handle before splitting

**Application to CeutIA-Serpiente:**
- Walk-forward validation is the standard for CeutIA-Serpiente's temporal evaluation
- Nested CV prevents selection bias in hyperparameter tuning
- Grouped CV is critical for healthcare data (patients, hospitals, regions)

**Limitations:**
- Technical blog, not peer-reviewed
- Vendor-affiliated (MetricGate)

**Independence Assessment:**
- **Rating: MODERATE INDEPENDENCE**

---

### Source 1.10: Machine Learning Mastery - Time Series Cross-Validation (2026)

**Title:** 5 Ways to Use Cross-Validation to Improve Time Series Models  
**Authors:** Jason Brownlee  
**Year:** 2026  
**Type:** Educational blog  
**URL:** https://machinelearningmastery.com/5-ways-to-use-cross-validation-to-improve-time-series-models/

**Key Findings/Methods:**
- Five practical CV patterns for realistic, leak-resistant time series evaluation
- Warning: Suspiciously stable validation scores across folds often signal leakage (real time series performance usually fluctuates)

**Application to CeutIA-Serpiente:**
- Performance stability across folds is a red flag for leakage
- Multiple CV patterns provide robustness checks

**Limitations:**
- Educational blog, not peer-reviewed
- Conceptual overview

**Independence Assessment:**
- Independent educational resource; high independence
- **Rating: HIGH INDEPENDENCE**

---

### Source 1.11: Temporal Book - Evaluation Protocols, Backtesting, and Data Leakage

**Title:** Evaluation Protocols, Backtesting, and Data Leakage (Section 2.6)  
**Authors:** Not specified  
**Year:** Not specified  
**Type:** Online book/educational resource  
**URL:** http://temporalbook.apartsin.com/part-1-foundations/module-02-temporal-data-engineering/section-2.6.html

**Key Findings/Methods:**
- Why i.i.d. cross-validation is invalid for time series
- Time-aware validation with walk-forward and rolling backtesting
- **Purging and embargo**: Remove from training set any sample whose label interval overlaps test interval; embargo drops short gap of training samples immediately after test block (serial correlation lets information leak backward across boundary)
- Forecast metrics and their pitfalls
- Realism checks: costs, non-stationarity, multiple testing, naive baselines separate trustworthy backtests from unreliable ones
- Simplest honest protocol: single temporal hold-out (train on first portion, test on tail, never reverse)
- Every transform must fit inside temporal training block; time-aware splitter decides what counts as future

**Application to CeutIA-Serpiente:**
- Purging and embargo are critical for overlapping prediction horizons (common in healthcare forecasting)
- Temporal hold-out is the minimum standard; walk-forward is preferred
- All transforms must be inside training block to prevent leakage

**Limitations:**
- Online book, not peer-reviewed
- Conceptual focus

**Independence Assessment:**
- Independent educational resource; high independence
- **Rating: HIGH INDEPENDENCE**

---

## TOPIC 2: REPRODUCIBLE BACKTESTING

### Source 2.1: Portfolio Optimization Book - Seven Sins of Quantitative Investing (2025)

**Title:** 8.2 The Seven Sins of Quantitative Investing  
**Authors:** Not specified (cites Luo et al., 2014; López de Prado, 2018a)  
**Year:** 2025  
**Type:** Online book chapter  
**URL:** https://portfoliooptimizationbook.com/book/8.2-seven-sins.html

**Key Findings/Methods:**
- **Seven Sins** (from Luo et al., 2014, Deutsche Bank): survivorship bias; look-ahead bias; storytelling bias; overfitting and data snooping bias; turnover and transaction cost; outliers; asymmetric pattern and shorting cost
- Data snooping antidote: split data into in-sample and out-of-sample; but test data can inadvertently become training data through iteration
- Avoid overfitting: avoid fine-tuning parameters, perform sensitivity analysis, and ultimately test on new data/paper/live data

**Application to CeutIA-Serpiente:**
- Seven sins framework provides a comprehensive backtesting audit checklist
- Data snooping requires strict in-sample/out-of-sample discipline
- Sensitivity analysis is mandatory before deployment
- Survivorship bias applies to healthcare (e.g., only analyzing hospitals that still exist, excluding closed clinics)

**Limitations:**
- Online book, not peer-reviewed journal
- Synthesizes prior work (Luo et al., 2014; López de Prado, 2018a)

**Independence Assessment:**
- Independent educational resource; cites peer-reviewed sources
- **Rating: HIGH INDEPENDENCE**

---

## TOPIC 3: OUT-OF-SAMPLE EVALUATION

### Source 3.1: Journal of Forecasting - Optimal Out-of-Sample Forecast Evaluation (2023)

**Title:** Optimal out-of-sample forecast evaluation under stationarity  
**Authors:** Staněk Filip  
**Year:** 2023  
**Type:** Peer-reviewed journal article  
**DOI:** 10.1002/for.3013  
**URL:** https://onlinelibrary.wiley.com/doi/full/10.1002/for.3013

**Key Findings/Methods:**
- Common practice: split time series into in-sample and pseudo-out-of-sample segments; estimate out-of-sample loss over pseudo-out-of-sample segment
- Proposed alternative estimator uses in- and out-of-sample criteria via affine weights and is BLUE under stationarity
- Applied to Diebold-Mariano tests with power gains and finite-sample robustness
- Evaluated on M4 forecasting data

**Application to CeutIA-Serpiente:**
- Can improve out-of-sample evaluation efficiency for stationary healthcare series
- Diebold-Mariano tests are relevant for predictive-model comparison

**Limitations:**
- Assumes stationarity for theoretical optimality
- Single-author study

**Independence Assessment:**
- Peer-reviewed journal article
- **Rating: HIGH INDEPENDENCE**

---

### Source 3.2: arXiv - Evaluating Time Series Forecasting Models (2019)

**Title:** Evaluating time series forecasting models: An empirical study on performance estimation methods  
**Authors:** Vitor Cerqueira, Luis Torgo, Igor Mozetič  
**Year:** 2019  
**Type:** Preprint (arXiv)  
**URL:** https://arxiv.org/pdf/1905.11744.pdf

**Key Findings/Methods:**
- Compares out-of-sample holdout methods and cross-validation variants for time-series performance estimation
- Studies 62 real-world time series and synthetic stationary series
- Real-world non-stationary series favored replicated holdout/holdout methods; some CV procedures underestimated error

**Application to CeutIA-Serpiente:**
- For non-stationary healthcare series, forward/OOS evaluation should be preferred to naive random CV
- Selection should reflect risk tolerance and deployment conditions

**Limitations:**
- Preprint status in supplied source; later publication should be checked before treating it as final peer-reviewed evidence
- Healthcare-specific validation is still required

**Independence Assessment:**
- **Rating: HIGH INDEPENDENCE**

---

### Source 3.3: FAU Discussion Papers - Model Validation for Non-Stationary Time Series (2019)

**Title:** A comparison of machine learning model validation schemes for non-stationary time series data  
**Authors:** Matthias Schnaubelt  
**Year:** 2019  
**Type:** Discussion paper (FAU)  
**URL:** https://www.econstor.eu/bitstream/10419/209136/1/1684440068.pdf

**Key Findings/Methods:**
- Compares random, blocked, h-blocked, rolling-origin, rolling-window, growing-window and last-block validation schemes under controlled non-stationarity
- Forward-validation generally produced better estimates of future error; randomized CV performed poorly as non-stationarity increased
- Real-world S&P 500 validation showed similar differences

**Application to CeutIA-Serpiente:**
- Forward-validation is strongly preferred for non-stationary temporal data
- Last-block is a simple baseline; rolling-origin/growing-window provide richer evaluation

**Limitations:**
- Discussion paper and finance-domain validation

**Independence Assessment:**
- University source
- **Rating: HIGH INDEPENDENCE**

---

## TOPIC 4: REVISION OF HISTORICAL SERIES AND DATA REVISIONS

### Source 4.1: Oxford Bulletin of Economics and Statistics - Real-Time Data, Revisions and Predictive Ability (2025)

**Title:** Real-Time Data, Revisions and the Predictive Ability of DSGE Models  
**Year:** 2025  
**Type:** Peer-reviewed journal article  
**DOI:** 10.1111/obes.12677  
**URL:** https://onlinelibrary.wiley.com/doi/full/10.1111/obes.12677

**Key Findings/Methods:**
- Evaluates real-time versus revised macroeconomic data and their effect on forecasting performance
- Revision effects vary by region, variable and historical period
- Predictive accuracy can change materially when revised observations replace real-time vintages

**Application to CeutIA-Serpiente:**
- Backtesting must reconstruct the information set actually available at each forecast origin
- Healthcare data revisions may similarly affect apparent historical performance
- Crisis periods can have distinct revision behavior and should not be treated as homogeneous

**Limitations:**
- Macroeconomic rather than healthcare data
- DSGE rather than ML models

**Independence Assessment:**
- Peer-reviewed journal article
- **Rating: HIGH INDEPENDENCE**

---

## TOPIC 5: CHANGES IN INDICATOR DEFINITIONS AND METHODOLOGY

### Source 5.1: Oxford Academic - Structural Breaks in Time Series (2018)

**Title:** Structural Breaks in Time Series  
**Year:** 2018  
**Type:** Book chapter (Oxford Academic)  
**URL:** https://academic.oup.com/edited-volume/61801/chapter/546469021

**Key Findings/Methods:**
- Reviews estimation, testing and computation for models involving structural changes
- Covers methods for estimating break dates and determining the number of changes
- Includes retrospective/offline structural-break methods

**Application to CeutIA-Serpiente:**
- Methodology changes should be treated as potential structural breaks rather than ignored
- Break-date uncertainty should be represented explicitly

**Limitations:**
- Book chapter; econometric focus

**Independence Assessment:**
- Oxford Academic publication
- **Rating: HIGH INDEPENDENCE**

---

### Source 5.2: Journal of Time Series Analysis - Structural Breaks in Time Series (2013)

**Title:** Structural breaks in time series  
**Authors:** Aue  
**Year:** 2013  
**Type:** Peer-reviewed journal article  
**DOI:** 10.1111/j.1467-9892.2012.00819.x  
**URL:** https://onlinelibrary.wiley.com/doi/10.1111/j.1467-9892.2012.00819.x

**Key Findings/Methods:**
- Reviews structural-break procedures for serially dependent time series
- Covers CUSUM methods for changes in mean, variance and covariance/correlation structures
- Discusses parametric likelihood methods and multiple breaks

**Application to CeutIA-Serpiente:**
- CUSUM and related methods can support break detection in long healthcare series
- Multiple-break detection is relevant where policies, coding systems or measurement protocols change repeatedly

**Limitations:**
- Older but foundational review
- Econometric focus

**Independence Assessment:**
- Peer-reviewed journal article
- **Rating: HIGH INDEPENDENCE**

---

### Source 5.3: Stata Journal - Testing and Estimating Structural Breaks (2025)

**Title:** Testing and estimating structural breaks in time series and panel data  
**Year:** 2025  
**Type:** Peer-reviewed journal article  
**DOI:** 10.1177/1536867X251365449  
**URL:** https://journals.sagepub.com/doi/10.1177/1536867X251365449

**Key Findings/Methods:**
- Structural-change detection should identify whether breaks exist, their number and their locations
- The `xtbreak` tooling supports multiple breaks and confidence intervals for break dates

**Application to CeutIA-Serpiente:**
- Healthcare time series should detect major regime/methodology changes before assuming parameter stability
- Confidence intervals for break dates should feed uncertainty handling
- Python/R equivalents are required for production implementation

**Limitations:**
- Stata-specific tooling
- Healthcare adaptation remains necessary

**Independence Assessment:**
- Peer-reviewed journal article
- **Rating: HIGH INDEPENDENCE**

---

## SYNTHESIS AND RECOMMENDATIONS FOR CEUTIA-SERPIENTE

### Cross-Cutting Themes

1. **Temporal Integrity is Non-Negotiable:** Temporal leakage can materially inflate apparent predictive performance; all evaluation must respect the information set available at the forecast/decision origin.
2. **Real-Time Data Discipline:** Historical evaluation should use point-in-time or vintage data whenever revisions can occur.
3. **Forward-Validation for Non-Stationary Data:** Walk-forward, rolling-origin or related forward validation is preferable to naive randomized CV when the data-generating process evolves over time.
4. **Structural Break Detection and Handling:** Changes in measurement, coding, policy or data-generating mechanisms can create structural breaks that invalidate a single stationary evaluation regime.
5. **Data Snooping Defenses:** In-sample/out-of-sample separation, preregistration, sensitivity analysis and multiplicity-aware testing reduce retrospective optimization and overfitting.

### Recommended Framework for CeutIA-Serpiente

1. **Data Pipeline:**
   - Implement vintage/point-in-time data structures where historical revisions exist.
   - Enforce forecast-origin timestamps and publication/availability timestamps.
   - Fit preprocessing and feature transformations only on the training information set for each evaluation origin.

2. **Temporal Leakage Prevention:**
   - Apply the three-type leakage taxonomy as an audit framework.
   - Use temporal split or walk-forward validation rather than randomized i.i.d. splits for temporal data.
   - Implement purging and embargo where prediction horizons or label intervals overlap.
   - Explicitly lag rolling/expanding features according to the forecast horizon.

3. **Backtesting Protocol:**
   - Define temporal training/test boundaries before evaluation.
   - Use walk-forward/rolling-origin evaluation where deployment is sequential.
   - Record parameter sensitivity and alternative specifications.
   - Timestamp hypotheses and model-selection decisions to distinguish exploratory from confirmatory analysis.
   - Apply multiplicity-aware procedures when many candidate hypotheses are tested.

4. **Out-of-Sample Evaluation:**
   - Compare models using strictly out-of-sample predictions.
   - Use forecast-origin-aware metrics and model comparison tests where assumptions are satisfied.
   - Report performance by time regime, not only pooled averages.

5. **Data Revisions:**
   - Preserve data vintages where feasible.
   - Reconstruct the information set available at each historical decision point.
   - Distinguish original observations from subsequently revised observations.

6. **Structural Breaks:**
   - Detect candidate breaks using methods such as CUSUM or multiple-break procedures.
   - Record break dates and uncertainty.
   - Treat methodology/coding/policy changes as candidate regime boundaries.
   - Evaluate whether models remain valid across or within detected regimes.

### Limitations and Gaps

- Most supplied empirical sources are from finance, macroeconomics, software engineering or general ML rather than healthcare.
- Several supplied references are blogs, preprints or discussion papers and should not be weighted like peer-reviewed primary evidence.
- Python/R implementations of structural-break procedures still need explicit engineering selection and validation.
- Regulatory requirements for healthcare AI evaluation are not established by this package alone.

### Next Steps

1. Prioritize peer-reviewed healthcare-specific evidence on temporal leakage, backtesting and structural breaks.
2. Build vintage/point-in-time data infrastructure where source revisions occur.
3. Implement walk-forward validation with purging/embargo semantics.
4. Create a structural-break detection module with explicit uncertainty and regime metadata.
5. Establish a preregistration/evaluation manifest before model selection.
6. Validate the evaluation framework on datasets containing known temporal leakage, revisions and structural changes.

---

## REFERENCES (Verified DOIs/URLs supplied in the research package)

1. Mishra LN, Rangari A, Nagrare S, Nayak SK (2026). A taxonomy for detecting and preventing temporal data leakage in machine learning-based build prediction. PLoS One 21(5): e0340167. DOI: 10.1371/journal.pone.0340167
2. Staněk Filip (2023). Optimal out-of-sample forecast evaluation under stationarity. Journal of Forecasting. DOI: 10.1002/for.3013
3. Schnaubelt Matthias (2019). A comparison of machine learning model validation schemes for non-stationary time series data. FAU Discussion Papers in Economics, No. 11/2019. URL: https://www.econstor.eu/bitstream/10419/209136/1/1684440068.pdf
4. Real-Time Data, Revisions and the Predictive Ability of DSGE Models (2025). Oxford Bulletin of Economics and Statistics. DOI: 10.1111/obes.12677
5. Aue (2013). Structural breaks in time series. Journal of Time Series Analysis. DOI: 10.1111/j.1467-9892.2012.00819.x
6. Testing and estimating structural breaks in time series and panel data (2025). Stata Journal. DOI: 10.1177/1536867X251365449
7. Editorial: Data Segmentation in Time Series (2026). Journal of Time Series Analysis. DOI: 10.1111/jtsa.70055
8. Cerqueira V, Torgo L, Mozetič I (2019). Evaluating time series forecasting models: an empirical study on performance estimation methods. URL: https://arxiv.org/pdf/1905.11744.pdf
9. How Data Leakage Affects LSTM Evaluation Across Configurations (2025). arXiv:2512.06932.
10. How Good is That Forecast? The Nuances of Prediction (SAS Proceedings, 2018). URL: https://support.sas.com/resources/papers/proceedings18/1862-2018.pdf
11. Avoiding Look Ahead Bias in Time Series Modelling (Data Science Central, 2017). URL: https://www.datasciencecentral.com/avoiding-look-ahead-bias-in-time-series-modelling-1/
12. 3 Common Time Series Modeling Mistakes You Should Know (Towards Data Science, 2025). URL: https://towardsdatascience.com/3-common-time-series-modeling-mistakes-you-should-know-a126df24256f/
13. Time Series Cross-Validation: Preventing Leakage in GRU & SVR (Kuriko Iwai, 2026). URL: https://kuriko-iwai.com/research/advanced-cross-validation-techniques
14. Stop the spill: the blueprint for eradicating data leakage (Data Science at Microsoft, 2025). URL: https://medium.com/data-science-at-microsoft/stop-the-spill-the-blueprint-for-eradicating-data-leakage-6f924e543a95
15. Look-Ahead Bias in Rolling Window Features (MH Techin, 2024). URL: https://www.mhtechin.com/support/look-ahead-bias-in-rolling-window-features/
16. Cross-Validation Pitfalls to Avoid (MetricGate, 2025). URL: https://metricgate.com/blogs/cross-validation-pitfalls/
17. 5 Ways to Use Cross-Validation to Improve Time Series Models (Machine Learning Mastery, 2026). URL: https://machinelearningmastery.com/5-ways-to-use-cross-validation-to-improve-time-series-models/
18. Evaluation Protocols, Backtesting, and Data Leakage. URL: http://temporalbook.apartsin.com/part-1-foundations/module-02-temporal-data-engineering/section-2.6.html
19. 8.2 The Seven Sins of Quantitative Investing. URL: https://portfoliooptimizationbook.com/book/8.2-seven-sins.html
20. Structural Breaks in Time Series. Oxford Academic. URL: https://academic.oup.com/edited-volume/61801/chapter/546469021
21. Editorial: Data Segmentation in Time Series: Structural Breaks and Real-Time Monitoring. DOI: 10.1111/jtsa.70055

---

*Document generated: 2026-09-13*  
*For: CeutIA-Serpiente Project*  
*Author: AI Research Assistant*
