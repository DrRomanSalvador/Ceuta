"""Verified initial scientific corpus from the current Perplexity-derived block.

This is deliberately a seed, not a closed bibliography. Later ingestion appends
new versions/sources and relations without replacing prior scientific records.
"""
from __future__ import annotations

from hashlib import sha256

from .source_corpus import (
    CorpusEvidenceLevel,
    CorpusSourceType,
    ImpactRelation,
    RetrievalMetadata,
    ScientificImpactMap,
    ScientificRelation,
    ScientificSourceCorpus,
    ScientificSourceRecord,
    ValidationStatus,
)


RETRIEVER = "CeutIA scientific ingestion"
RETRIEVED_AT = "2026-09-15T00:00:00+00:00"


def _retrieval(url: str, identifier: str) -> RetrievalMetadata:
    # This fingerprint covers the verified bibliographic retrieval payload, not
    # the full article bytes. Full-text hashes must only be recorded when bytes
    # are actually retrieved and preserved.
    fingerprint = sha256(f"bibliographic:{identifier}|{url}".encode()).hexdigest()
    return RetrievalMetadata(RETRIEVED_AT, "verified_bibliographic_metadata", RETRIEVER, fingerprint, url)


def current_sources() -> tuple[ScientificSourceRecord, ...]:
    return (
        ScientificSourceRecord(
            source_id="sawada-2022-cry-wolf",
            title="Impact of cry wolf effects on social preparedness and the efficiency of flood early warning systems",
            authors=("Yohei Sawada", "Rin Kanai", "Hitomu Kotani"), year=2022,
            identifier="10.5194/hess-26-4265-2022",
            official_url="https://doi.org/10.5194/hess-26-4265-2022",
            source_type=CorpusSourceType.COMPLEX_SYSTEMS, evidence_level=CorpusEvidenceLevel.METHODOLOGICAL,
            methodology="stylized socio-hydrological model coupling flood dynamics, collective memory, trust and preparedness",
            population_context="flood early-warning systems and socially mediated preparedness",
            domain="early_warning",
            phenomenon=("cry_wolf", "trust_decay", "preparedness_decay", "false_alarms"),
            findings=("repeated false alarms can undermine warning credibility and preparedness",),
            limitations=("stylized model; deployment-specific behavioral effect requires prospective validation",),
            applicability=("warning systems where human trust and response are material",),
            relevant_mechanism=("asymmetric false-alarm cost", "credibility state", "outcome settlement"),
            ceutia_components=("early_warning_governance", "scientific_governance", "decision_control", "response_closure"),
            implementation_implications=("persist warning outcomes and update credibility", "make false alarms governance-relevant"),
            validation_requirements=("prospective trust/preparedness outcomes", "domain-specific policy calibration"),
            provenance="peer-reviewed HESS article; DOI-anchored bibliographic retrieval",
            retrieval=_retrieval("https://doi.org/10.5194/hess-26-4265-2022", "10.5194/hess-26-4265-2022"),
        ),
        ScientificSourceRecord(
            source_id="dakos-2012-csd-robustness",
            title="Robustness of variance and autocorrelation as indicators of critical slowing down",
            authors=("Vasilis Dakos",), year=2012,
            identifier="10.1890/11-0889.1",
            official_url="https://doi.org/10.1890/11-0889.1",
            source_type=CorpusSourceType.METHODOLOGICAL, evidence_level=CorpusEvidenceLevel.METHODOLOGICAL,
            methodology="analytical and simulation study of variance and autocorrelation near transitions",
            population_context="stochastically forced ecological and dynamical systems",
            domain="complex_systems",
            phenomenon=("critical_slowing_down", "variance", "autocorrelation", "false_positive", "sampling_limits"),
            findings=("autocorrelation can be more robust than variance under some conditions", "indicator behavior depends on noise and sampling"),
            limitations=("results concern specific dynamical assumptions; CSD is not universal",),
            applicability=("time-series resilience diagnostics with appropriate dynamical assumptions",),
            relevant_mechanism=("lag-1 autocorrelation", "variance diagnostic", "data-sufficiency gate"),
            ceutia_components=("early_warning_governance", "temporal_modeling", "uncertainty", "model_governance"),
            implementation_implications=("avoid treating variance increase as mandatory", "record sampling and noise assumptions"),
            validation_requirements=("domain-specific sensitivity analysis", "prospective transition outcomes"),
            provenance="peer-reviewed Ecology article; DOI-anchored bibliographic retrieval",
            retrieval=_retrieval("https://doi.org/10.1890/11-0889.1", "10.1890/11-0889.1"),
        ),
        ScientificSourceRecord(
            source_id="dakos-2014-resilience-indicators",
            title="Resilience indicators: prospects and limitations for early warnings of regime shifts",
            authors=("Vasilis Dakos", "Marten Scheffer", "Ellen H. van Nes", "et al."), year=2015,
            identifier="PMCID:PMC4247400",
            official_url="https://pmc.ncbi.nlm.nih.gov/articles/PMC4247400/",
            source_type=CorpusSourceType.METHODOLOGICAL, evidence_level=CorpusEvidenceLevel.METHODOLOGICAL,
            methodology="review and conceptual synthesis of resilience indicators and critical transitions",
            population_context="complex ecosystems and regime-shift early warnings",
            domain="complex_systems",
            phenomenon=("resilience", "critical_transition", "critical_slowing_down", "false_alarm", "missed_alarm"),
            findings=("variance and autocorrelation can indicate slowing recovery", "not all regime shifts are bifurcation-driven", "false positives and missed alarms are material"),
            limitations=("indicators are not forecasting tools per se", "stochastic regimes can mimic warning signals"),
            applicability=("supporting resilience evidence, not deterministic tipping-point prediction",),
            relevant_mechanism=("supporting-signal classification", "false-alarm control", "missed-alarm tracking"),
            ceutia_components=("early_warning_governance", "uncertainty", "release_review_abstain"),
            implementation_implications=("represent CSD as bounded supporting evidence", "retain no-alarm and false-alarm outcomes"),
            validation_requirements=("prospective regime-shift validation",),
            provenance="peer-reviewed methodological synthesis; PMC full-text landing page",
            retrieval=_retrieval("https://pmc.ncbi.nlm.nih.gov/articles/PMC4247400/", "PMCID:PMC4247400"),
        ),
        ScientificSourceRecord(
            source_id="dakos-2012-climate-robustness",
            title="Early warning of climate tipping points from critical slowing down: comparing methods to improve robustness",
            authors=("Vasilis Dakos", "S. R. Carpenter", "W. A. Brock", "et al."), year=2012,
            identifier="10.1098/rsta.2011.0304",
            official_url="https://doi.org/10.1098/rsta.2011.0304",
            source_type=CorpusSourceType.METHODOLOGICAL, evidence_level=CorpusEvidenceLevel.METHODOLOGICAL,
            methodology="comparative analysis of autocorrelation and detrended-fluctuation approaches under preprocessing choices",
            population_context="palaeoclimate records and climate model simulations",
            domain="complex_systems",
            phenomenon=("critical_slowing_down", "detrending_sensitivity", "window_sensitivity", "false_positive"),
            findings=("method choice and preprocessing can change early-warning results", "combining methods can improve robustness"),
            limitations=("tested systems and methods do not establish universal operational validity",),
            applicability=("time-series EWS pipelines where preprocessing sensitivity can be measured",),
            relevant_mechanism=("method ensemble", "sensitivity analysis", "preprocessing provenance"),
            ceutia_components=("temporal_modeling", "model_governance", "scientific_method_registry"),
            implementation_implications=("version preprocessing and method configuration", "test robustness across analytical choices"),
            validation_requirements=("prospective method comparison",),
            provenance="Philosophical Transactions of the Royal Society A; DOI-anchored retrieval",
            retrieval=_retrieval("https://doi.org/10.1098/rsta.2011.0304", "10.1098/rsta.2011.0304"),
        ),
        ScientificSourceRecord(
            source_id="false-positives-2019-ews",
            title="Systematically false positives in early warning signal analysis",
            authors=("J. Boettiger", "A. Hastings"), year=2019,
            identifier="10.1371/journal.pone.0211072",
            official_url="https://doi.org/10.1371/journal.pone.0211072",
            source_type=CorpusSourceType.METHODOLOGICAL, evidence_level=CorpusEvidenceLevel.METHODOLOGICAL,
            methodology="simulation-based assessment of statistical false positives in EWS analysis",
            population_context="time-series early warning signals for population collapse",
            domain="early_warning",
            phenomenon=("false_positive", "critical_slowing_down", "statistical_detection"),
            findings=("EWS analyses can produce systematic false positives",),
            limitations=("simulation and model assumptions constrain generalization",),
            applicability=("adversarial and sensitivity testing of EWS detectors",),
            relevant_mechanism=("false-positive testing", "adversarial signal validation"),
            ceutia_components=("early_warning_governance", "adversarial_robustness", "uncertainty"),
            implementation_implications=("include synthetic negative controls and false-positive tests",),
            validation_requirements=("external prospective false-positive rate estimation",),
            provenance="peer-reviewed PLOS ONE article; DOI-anchored retrieval",
            retrieval=_retrieval("https://doi.org/10.1371/journal.pone.0211072", "10.1371/journal.pone.0211072"),
        ),
        ScientificSourceRecord(
            source_id="forestal-2020-prediction-markets",
            title="Prediction Markets: A Systematic Review and Meta-Analysis",
            authors=("Roberto Louis Forestal", "Peng Cheng Zhang", "Shih-Ming Pi"), year=2020,
            identifier="ICEB-2020-51",
            official_url="https://aisel.aisnet.org/iceb2020/51/",
            source_type=CorpusSourceType.META_ANALYSIS, evidence_level=CorpusEvidenceLevel.META_ANALYTIC,
            methodology="PRISMA-guided systematic review and meta-analysis of prediction-market studies",
            population_context="prediction-market forecasting studies across internal and public use",
            domain="forecasting",
            phenomenon=("prediction_market_accuracy", "forecast_aggregation", "heterogeneity"),
            findings=("included studies reported a mean 79% accuracy advantage over alternatives",),
            limitations=("study inclusion/quality judgments were partly subjective", "heterogeneity and market context limit universal transfer"),
            applicability=("benchmark/ensemble input where market integrity and liquidity are established",),
            relevant_mechanism=("benchmark scoring", "forecast aggregation", "market integrity gate"),
            ceutia_components=("forecasting", "calibration", "scientific_governance", "model_disagreement"),
            implementation_implications=("compare market forecasts against CeutIA forecasts rather than treating markets as truth",),
            validation_requirements=("domain-specific out-of-sample score comparison", "liquidity/integrity stratification"),
            provenance="ICEB 2020 proceedings; official AIS eLibrary record",
            retrieval=_retrieval("https://aisel.aisnet.org/iceb2020/51/", "ICEB-2020-51"),
        ),
        ScientificSourceRecord(
            source_id="forin-2019-ews",
            title="Early Warning Systems: Lost in Translation or Late by Definition? A FORIN Approach",
            authors=("Virginia Alcántara-Ayala", "Anthony Oliver-Smith"), year=2019,
            identifier="10.1007/s13753-019-00231-3",
            official_url="https://doi.org/10.1007/s13753-019-00231-3",
            source_type=CorpusSourceType.EARLY_WARNING, evidence_level=CorpusEvidenceLevel.METHODOLOGICAL,
            methodology="FORIN-based conceptual and causal analysis of early-warning design",
            population_context="disaster risk, exposure, vulnerability, governance and early-warning systems",
            domain="disaster_risk",
            phenomenon=("vulnerability", "root_causes", "risk_drivers", "early_warning", "transdisciplinary_governance"),
            findings=("hazard-only warning design can miss root causes and risk drivers", "integrated and transdisciplinary analysis is required"),
            limitations=("framework is methodological and context-dependent; quantitative effect size is not established",),
            applicability=("high-stakes warnings involving social vulnerability and governance",),
            relevant_mechanism=("vulnerability profiling", "root-cause mapping", "causal trajectory analysis"),
            ceutia_components=("causal_inference", "early_warning_governance", "decision_governance", "response_design"),
            implementation_implications=("attach vulnerability and structural-driver context to warning assessments", "separate hazard probability from social risk"),
            validation_requirements=("prospective response and harm outcomes", "participatory/domain validation"),
            provenance="International Journal of Disaster Risk Science; DOI-anchored retrieval",
            retrieval=_retrieval("https://doi.org/10.1007/s13753-019-00231-3", "10.1007/s13753-019-00231-3"),
        ),
        ScientificSourceRecord(
            source_id="forin-2023-systematic-review",
            title="A Systematic Review of Forensic Approaches to Disasters: Gaps and Challenges",
            authors=("Fraser et al.",), year=2023,
            identifier="10.1007/s13753-023-00515-9",
            official_url="https://doi.org/10.1007/s13753-023-00515-9",
            source_type=CorpusSourceType.SYSTEMATIC_REVIEW, evidence_level=CorpusEvidenceLevel.SYSTEMATIC_REVIEW,
            methodology="qualitative systematic review of forensic disaster studies",
            population_context="156 selected scientific articles covering FORIN, PERC, DDRC and FDA approaches",
            domain="disaster_risk",
            phenomenon=("root_cause_analysis", "vulnerability", "participation", "transdisciplinarity"),
            findings=("forensic approaches remain sparse and often isolated", "participatory and transdisciplinary methods are identified as a gap"),
            limitations=("qualitative synthesis; limited empirical quantitative comparison of forensic methods",),
            applicability=("architecture for structured root-cause and vulnerability evidence",),
            relevant_mechanism=("forensic evidence graph", "participatory evidence provenance", "causal root-driver mapping"),
            ceutia_components=("scientific_knowledge", "causal_inference", "evidence_hierarchy", "provenance"),
            implementation_implications=("represent root causes, drivers and participation as first-class evidence dimensions",),
            validation_requirements=("domain-specific prospective forensic case validation",),
            provenance="International Journal of Disaster Risk Science; DOI-anchored retrieval",
            retrieval=_retrieval("https://doi.org/10.1007/s13753-023-00515-9", "10.1007/s13753-023-00515-9"),
        ),
    )


def current_impacts() -> tuple[ScientificImpactMap, ...]:
    return (
        ScientificImpactMap(
            impact_id="impact-early-warning-composition-v1",
            source_ids=("sawada-2022-cry-wolf", "dakos-2012-csd-robustness", "false-positives-2019-ews", "forin-2019-ews"),
            phenomenon="high-stakes early-warning reliability",
            supported_claim="warning quality is jointly constrained by signal validity, false-alarm cost, social credibility and vulnerability context",
            evidence_level="mixed_methodological",
            valid_context="high-stakes early-warning systems where warnings trigger human or institutional response",
            limitations=("the compositional effect size in CeutIA is unknown", "CSD is not universal", "behavioral parameters are deployment-specific"),
            mechanism=("asymmetric warning credibility", "supporting CSD diagnostics", "false-positive controls", "vulnerability-aware response design"),
            existing_components=("early_warning_governance", "scientific_governance", "causal_inference", "response_closure"),
            contradictions_or_modifications=("CSD cannot be treated as a standalone tipping-point detector", "hazard probability cannot stand in for social risk"),
            missing_capabilities=("prospective compositional validation", "participatory vulnerability evidence", "rolling method sensitivity analysis"),
            implementation_now=("persistent scientific impact map", "cross-source relation graph", "adversarial false-positive contracts"),
            integration_requirements=("evidence provenance", "governance signal", "outcome settlement", "decision lineage"),
            tests_required=("false alarms", "missed alarms", "CSD confounding", "vulnerability perturbation", "composition conflict"),
            internal_validation=("deterministic persistence and integrity tests", "governance gating tests"),
            external_validation=("prospective warning outcomes and human response",),
            dependencies=("source provenance", "temporal point-in-time evidence", "response closure"),
            mission_queue=("build prospective early-warning validation harness", "add method-sensitivity ensemble for CSD", "add human approval state for high-stakes warnings"),
            assumptions=("warning outcomes can be objectively settled",),
            uncertainty=("deployment-specific trust dynamics", "causal effect of warning architecture"),
            identifiability="mechanism components are implementable; end-to-end causal benefit requires prospective outcomes",
            applicability_boundary="do not generalize beyond domains with measurable warning outcomes and response pathways",
            validation_status=ValidationStatus.PROSPECTIVE_REQUIRED,
        ),
        ScientificImpactMap(
            impact_id="impact-forecast-benchmark-v1",
            source_ids=("forestal-2020-prediction-markets",),
            phenomenon="forecast aggregation benchmark",
            supported_claim="prediction markets can provide a useful comparative forecasting benchmark under valid market conditions",
            evidence_level="meta_analytic",
            valid_context="domains where market probability is observable, liquid and integrity-checked",
            limitations=("reported 79% average advantage is heterogeneous and not a universal guarantee",),
            mechanism=("benchmark Brier/log score", "calibration comparison", "market integrity gate"),
            existing_components=("forecasting", "calibration", "model_governance"),
            contradictions_or_modifications=("market forecasts are benchmark evidence, not causal truth or authority"),
            missing_capabilities=("durable market-vs-CeutIA settlement scorer",),
            implementation_now=("market observation provenance and integrity fields already exist",),
            integration_requirements=("outcome settlement", "point-in-time market snapshot", "forecast identity"),
            tests_required=("invalid liquidity", "tampered market record", "Brier/log score comparison"),
            internal_validation=("schema and integrity validation"),
            external_validation=("out-of-sample comparative forecasting performance"),
            dependencies=("calibration", "truth settlement", "temporal integrity"),
            mission_queue=("implement market benchmark settlement and calibration comparison",),
            assumptions=("market probability is a genuine forecast at decision time",),
            uncertainty=("market selection and liquidity bias",),
            identifiability="comparative accuracy is measurable after outcomes settle; causal superiority is not identified",
            applicability_boundary="only use as benchmark where integrity and liquidity criteria are met",
            validation_status=ValidationStatus.IMPLEMENTED,
        ),
    )


def install_current_corpus(corpus: ScientificSourceCorpus) -> None:
    for source in current_sources():
        try:
            corpus.register(source)
        except ValueError as exc:
            if "already exists" not in str(exc):
                raise
    for relation in (
        ScientificRelation("dakos-2012-csd-robustness", "dakos-2014-resilience-indicators", ImpactRelation.COMPLEMENTS, "robustness analysis complements the broader resilience synthesis"),
        ScientificRelation("dakos-2012-climate-robustness", "false-positives-2019-ews", ImpactRelation.COMPLEMENTS, "method sensitivity and systematic false positives address related detection failure modes"),
        ScientificRelation("sawada-2022-cry-wolf", "forin-2019-ews", ImpactRelation.COMPLEMENTS, "social response credibility and vulnerability/root-cause framing jointly constrain warning effectiveness"),
        ScientificRelation("forestal-2020-prediction-markets", "dakos-2012-csd-robustness", ImpactRelation.COMPLEMENTS, "forecast benchmark evidence and dynamical diagnostics answer different questions"),
    ):
        corpus.add_relation(relation)
    for impact in current_impacts():
        try:
            corpus.add_impact(impact)
        except Exception as exc:
            if "UNIQUE constraint" not in str(exc):
                raise


__all__ = ["current_impacts", "current_sources", "install_current_corpus"]
