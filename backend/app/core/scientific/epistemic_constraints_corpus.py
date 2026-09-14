"""Cross-disciplinary constraint corpus beyond the initial EWS/DMDU/Goodhart blocks.

Records are deliberately conservative about bibliographic certainty. Where the
received material was a conceptual/user-supplied constraint rather than a fully
verified bibliographic record, the identifier explicitly says so instead of
inventing metadata.
"""
from __future__ import annotations

from .source_corpus import (
    CorpusEvidenceLevel,
    CorpusSourceType,
    ImpactRelation,
    ScientificImpactMap,
    ScientificRelation,
    ScientificSourceCorpus,
    ScientificSourceRecord,
    ValidationStatus,
)


def register_epistemic_constraints_block(corpus: ScientificSourceCorpus) -> None:
    records = (
        ScientificSourceRecord(
            "wolpert-macready-1997-no-free-lunch", "No Free Lunch Theorems for Optimization",
            ("David H. Wolpert", "William G. Macready"), 1997, "10.1109/4235.585893",
            "https://doi.org/10.1109/4235.585893", CorpusSourceType.METHODOLOGICAL,
            CorpusEvidenceLevel.METHODOLOGICAL,
            "formal optimization theorem over problem distributions", "optimization and search", "model_selection",
            ("no_free_lunch", "problem_distribution", "assumption_dependence"),
            ("universal algorithmic superiority cannot be claimed without restricting the problem distribution",),
            ("formal theorem concerns averaged performance over specified problem classes; it does not imply all practical models are equally useful",),
            ("model selection with explicit domain assumptions and validation distributions",),
            ("assumption_registry", "out_of_distribution_detection", "prospective_validation"),
            ("model_governance", "scientific_governance", "forecasting"),
            ("require model-domain assumptions and validation-distribution metadata", "do not promote one model as universally optimal"),
            ("prospective domain-transfer validation",),
            "peer-reviewed IEEE Transactions on Evolutionary Computation; DOI-anchored bibliographic retrieval",
            question_types=("model_selection", "forecasting", "optimization"), risk_levels=("high", "critical"),
        ),
        ScientificSourceRecord(
            "pearl-2009-causality", "Causality: Models, Reasoning, and Inference", ("Judea Pearl",), 2009,
            "ISBN:9780521895606", "", CorpusSourceType.CAUSAL_INFERENCE, CorpusEvidenceLevel.METHODOLOGICAL,
            "structural causal models, graphical identification and counterfactual reasoning", "causal inference", "causal_inference",
            ("causal_identifiability", "confounding", "counterfactuals", "assumptions"),
            ("causal effects are identified only under explicit structural/graphical assumptions",),
            ("identification assumptions can be substantively untestable from observational data alone",),
            ("causal questions with an explicit estimand and identification strategy",),
            ("causal_identification_contract", "counterfactual_reasoning", "sensitivity_analysis"),
            ("causal_inference", "decision_governance", "intervention_outcomes"),
            ("persist estimand and assumptions", "downgrade causal claims when identification is not established"),
            ("external identification and prospective causal validation",),
            "bibliographic record supplied in the received causal-inference block; exact edition identifier retained",
            question_types=("causal_effect", "intervention", "counterfactual"), risk_levels=("high", "critical"),
        ),
        ScientificSourceRecord(
            "early-warning-impossibility-constraint", "Early-warning evaluation identification constraint under successful prevention", (), 2020,
            "user-supplied:early-warning-impossibility", "", CorpusSourceType.EARLY_WARNING, CorpusEvidenceLevel.CONTEXTUAL,
            "conceptual identification argument concerning intervention-contaminated outcome labels", "early-warning and prevention", "early_warning",
            ("successful_prevention", "false_positive_ambiguity", "counterfactual_identification"),
            ("an averted event cannot be scored as an ordinary false positive without a defensible counterfactual",),
            ("this is an evaluation-identification constraint, not a theorem that early warnings are impossible",),
            ("warning systems whose alerts change the outcome process",),
            ("intervention-aware_outcome_ledger", "shadow_validation", "counterfactual_contract"),
            ("early_warning_governance", "intervention_outcomes", "response_closure"),
            ("separate ordinary prediction scoring from prevention effectiveness",),
            ("prospective counterfactual or intervention-independent validation",),
            "received user-supplied scientific constraint; intentionally not upgraded to a peer-reviewed bibliographic claim",
            validation_requirements=("prospective counterfactual identification", "intervention-independent control lane"),
        ),
        ScientificSourceRecord(
            "reference-class-forecasting-constraint", "Reference-class constraint for probabilities of unique or weakly comparable events", (), 2020,
            "user-supplied:reference-class-problem", "", CorpusSourceType.DECISION_THEORY, CorpusEvidenceLevel.CONTEXTUAL,
            "epistemic reference-class constraint", "forecasting unique events", "forecasting",
            ("reference_class", "uniqueness", "conditional_probability", "applicability_boundary"),
            ("probabilities for unique events require an explicit conditioning/reference class or an explicitly conditional model",),
            ("a reference class is a modeling choice and may itself be uncertain; absence of a stable class does not logically prohibit all probability statements",),
            ("unique crises and weakly recurrent geopolitical/social events",),
            ("reference_class_governance", "applicability_boundary", "graceful_degradation"),
            ("forecasting", "scientific_governance", "decision_governance"),
            ("persist reference-class identity, support size and applicability", "avoid unconditional probability claims outside observed support"),
            ("prospective calibration by declared reference class",),
            "received user-supplied constraint; no bibliographic metadata invented",
            question_types=("forecasting", "risk_assessment"), risk_levels=("high", "critical"),
        ),
        ScientificSourceRecord(
            "taleb-2007-black-swan", "The Black Swan: The Impact of the Highly Improbable", ("Nassim Nicholas Taleb",), 2007,
            "ISBN:9781400063512", "", CorpusSourceType.DECISION_THEORY, CorpusEvidenceLevel.CONTEXTUAL,
            "argument concerning model risk, rare events and retrospective explanatory overreach", "extreme/novel events", "risk",
            ("novelty", "tail_risk", "model_uncertainty", "retrospective_bias"),
            ("systems should not assume historical frequency models exhaust extreme-event risk",),
            ("claims about prediction of unprecedented events are contested; operational value is better framed as robustness/resilience than universal impossibility",),
            ("high-impact low-frequency and structurally novel events",),
            ("novelty_detection", "robust_decision", "resilience", "stress_testing"),
            ("decision_governance", "robust_decision", "nonstationarity"),
            ("stress strategies outside historical central tendency", "avoid treating historical extrapolation as certainty"),
            ("prospective tail-event and resilience validation",),
            "received user-supplied source and critique; conceptual constraint retained without treating contested claims as theorem",
            risk_levels=("high", "critical"),
        ),
        ScientificSourceRecord(
            "dakos-2026-ews-overview", "Early Warning Signals in Ecological Time-Series", ("Vasilis Dakos",), 2026,
            "10.3390/e28060628", "https://doi.org/10.3390/e28060628", CorpusSourceType.SYSTEMATIC_REVIEW,
            CorpusEvidenceLevel.METHODOLOGICAL,
            "overview of early-warning signal methods and assumptions", "ecological time series", "early_warning",
            ("critical_slowing_down", "method_selection", "false_positive", "nonstationarity"),
            ("early-warning indicators are conditional diagnostics whose interpretation depends on dynamics, noise and preprocessing",),
            ("ecological focus limits direct transfer to social systems",),
            ("supporting early-warning diagnostics with explicit assumptions",),
            ("method_ensemble", "sensitivity_analysis", "false_positive_controls"),
            ("early_warning_governance", "scientific_method_registry"),
            ("retain method/preprocessing provenance and avoid standalone CSD release gates",),
            ("prospective domain-specific validation",),
            "peer-reviewed overview; DOI-anchored bibliographic retrieval",
        ),
        ScientificSourceRecord(
            "forin-2016-disaster-forensics", "Disaster Forensics: Understanding Root Cause and Complex Causality", (), 2016,
            "10.1007/978-3-319-41849-0", "https://doi.org/10.1007/978-3-319-41849-0", CorpusSourceType.EARLY_WARNING,
            CorpusEvidenceLevel.METHODOLOGICAL,
            "forensic disaster analysis and complex causality", "disaster causation and vulnerability", "disaster_risk",
            ("root_causes", "complex_causality", "vulnerability", "forensics"),
            ("disaster outcomes can reflect interacting root causes and vulnerability pathways rather than hazard intensity alone",),
            ("forensic causal reconstruction is context-specific and does not automatically identify counterfactual effects",),
            ("post-event and prospective risk analysis",),
            ("root_cause_graph", "vulnerability_profile", "causal_boundary"),
            ("causal_inference", "early_warning_governance", "response_closure"),
            ("persist root-driver relations and causal uncertainty",),
            ("prospective forensic case validation",),
            "peer-reviewed Springer volume; DOI-anchored bibliographic retrieval",
        ),
        ScientificSourceRecord(
            "bussiere-early-warning-evaluation", "Early-warning evaluation impossibility/selection-bias constraint", (), 2020,
            "user-supplied:bussiere-icmaif-early-warning", "", CorpusSourceType.EARLY_WARNING, CorpusEvidenceLevel.CONTEXTUAL,
            "conceptual early-warning evaluation under intervention and selection", "financial/early-warning systems", "early_warning",
            ("selection_bias", "intervention", "counterfactual", "evaluation"),
            ("observed outcomes can be altered by the warning itself, so naive accuracy estimates can be biased",),
            ("exact scope depends on the supplied source and deployment design",),
            ("intervention-bearing warning systems",),
            ("intervention_independent_validation", "counterfactual_outcome_ledger"),
            ("early_warning_governance", "intervention_outcomes", "validation"),
            ("separate prediction and prevention metrics",),
            ("prospective validation with intervention-aware labels",),
            "received user-supplied scientific source block; bibliographic metadata intentionally conservative",
        ),
        ScientificSourceRecord(
            "smith-1995-performance-data", "On the unintended consequences of publishing performance data", ("Peter Smith",), 1995,
            "user-supplied:smith-1995-performance-data", "", CorpusSourceType.OBSERVATIONAL, CorpusEvidenceLevel.OBSERVATIONAL,
            "analysis of behavioral responses to public performance information", "performance measurement", "performance_measurement",
            ("publication_effects", "gaming", "selection", "target_response"),
            ("publishing metrics can change behavior and thereby alter the measurement process",),
            ("received bibliographic metadata was not fully verified in-session",),
            ("public metrics linked to allocation or reputation",),
            ("measurement_exposure_ledger", "metric_reactivity"),
            ("metric_reactivity", "scientific_governance"),
            ("treat publication as an intervention exposure",),
            ("prospective outcome and gaming validation",),
            "received source reference; metadata kept explicitly provisional",
        ),
        ScientificSourceRecord(
            "model-collapse-parallel-constraint", "Model collapse and recursive data-generation risk as a parallel reflexivity constraint", (), 2023,
            "user-supplied:model-collapse-parallel", "", CorpusSourceType.METHODOLOGICAL, CorpusEvidenceLevel.CONTEXTUAL,
            "received parallel between recursive synthetic data use and information degradation", "machine-learning training data", "machine_learning",
            ("recursive_training", "distribution_shift", "information_loss"),
            ("repeated dependence on model-generated data can create distributional degradation under some training regimes",),
            ("parallel is not evidence that CeutIA will collapse; direct mechanism and data lineage must be measured",),
            ("ML systems with recursive/generated-data exposure",),
            ("data_lineage", "synthetic_data_exposure", "distribution_monitoring"),
            ("model_governance", "provenance", "nonstationarity"),
            ("record training-data origin and monitor distributional degradation",),
            ("prospective model/data validation",),
            "received conceptual parallel; not treated as direct empirical evidence for CeutIA",
        ),
    )
    for record in records:
        try:
            corpus.register(record)
        except ValueError as exc:
            if "already exists" not in str(exc):
                raise

    for relation in (
        ScientificRelation("wolpert-macready-1997-no-free-lunch", "dmdu-rdm-pandemic-2023", ImpactRelation.COMPLEMENTS, "domain assumptions and robust decision making address different aspects of model uncertainty"),
        ScientificRelation("pearl-2009-causality", "causal-generalizability-bareinboim", ImpactRelation.COMPLEMENTS, "identification and transportability are complementary causal constraints"),
        ScientificRelation("early-warning-impossibility-constraint", "sawada-2022-cry-wolf", ImpactRelation.MODIFIES, "warning outcomes and credibility must be interpreted jointly with intervention effects"),
        ScientificRelation("reference-class-forecasting-constraint", "wolpert-macready-1997-no-free-lunch", ImpactRelation.COMPLEMENTS, "both constrain unqualified generalization but address different uncertainty sources"),
        ScientificRelation("taleb-2007-black-swan", "dakos-2026-ews-overview", ImpactRelation.COMPLEMENTS, "novelty and tail-risk caution complements conditional early-warning diagnostics"),
        ScientificRelation("forin-2016-disaster-forensics", "forin-2019-ews", ImpactRelation.SUPPORTS, "forensic root-cause analysis complements vulnerability-aware warning design"),
        ScientificRelation("smith-1995-performance-data", "bevan-hood-2006-target-gaming", ImpactRelation.COMPLEMENTS, "public performance information and target gaming are linked reflexive mechanisms"),
        ScientificRelation("model-collapse-parallel-constraint", "bevan-hood-2006-target-gaming", ImpactRelation.TRANSLATES, "both motivate monitoring for recursive adaptation to the measurement process, without asserting identical mechanisms"),
    ):
        try:
            corpus.add_relation(relation)
        except KeyError:
            pass

    corpus.add_impact(ScientificImpactMap(
        "impact-cross-cutting-epistemic-constraints-v1",
        tuple(record.source_id for record in records),
        "generalization, causality, novelty and reflexive evaluation constraints",
        "CeutIA must condition claims on reference classes, observed support, causal identification and intervention-aware outcomes rather than treating historical fit as universal validity.",
        "mixed_methodological_contextual", "adaptive, high-stakes decisions under non-stationarity and intervention",
        ("constraints are not interchangeable theorems", "thresholds require prospective validation", "contested claims are represented as robustness constraints"),
        ("reference class governance", "out-of-distribution support checks", "causal identification contract", "intervention-independent validation", "robustness gates"),
        ("scientific_governance", "decision_lifecycle", "model_governance", "validation", "provenance"),
        ("historical evidence was not uniformly conditioned on explicit applicability support",),
        ("persist reference class and observed support", "fail closed on unsupported extrapolation", "separate causal from descriptive claims", "track intervention-contaminated outcomes"),
        ("map mechanisms into RELEASE/REVIEW_REQUIRED/ABSTAIN", "retain provenance and method versions in runtime lineage"),
        ("reference-class boundary tests", "OOD/extrapolation tests", "causal-assumption tests", "intervention-independent scoring tests"),
        ("deterministic unit and persistence tests are possible now",),
        ("prospective domain transfer, causal and operational validation remain required",),
        ("explicit reference class", "observed feature support", "intervention outcome observability"),
        ("mission-cross-cutting-scientific-runtime-v1",),
        assumptions=("deployment context is explicitly declared", "support ranges are measured without leakage"),
        uncertainty=("novel events may invalidate reference classes",),
        identifiability="causal claims remain conditional on explicit identification assumptions",
        applicability_boundary="adaptive, high-stakes decisions where extrapolation and intervention feedback are material",
        validation_status=ValidationStatus.PROSPECTIVE_REQUIRED,
    ))


__all__ = ["register_epistemic_constraints_block"]
