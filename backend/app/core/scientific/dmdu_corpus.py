"""Seed records for the newly received DMDU/ensemble/causal block.

The records intentionally preserve methodological limits: DMDU does not make
futures probabilistic; BMA requires proper validation likelihoods; causal ML
does not solve unobserved confounding; and early-warning signals remain
context-dependent.
"""
from __future__ import annotations

from .source_corpus import (
    CorpusEvidenceLevel,
    CorpusSourceType,
    ScientificImpactMap,
    ScientificSourceCorpus,
    ScientificSourceRecord,
)


def register_dmdu_block(corpus: ScientificSourceCorpus) -> None:
    records = (
        ScientificSourceRecord(
            "dmdu-rdm-pandemic-2023",
            "Decision making under deep uncertainty for pandemic policy planning",
            (), 2023, "https://pmc.ncbi.nlm.nih.gov/articles/PMC10156381/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10156381/",
            CorpusSourceType.DECISION_THEORY, CorpusEvidenceLevel.METHODOLOGICAL,
            "decision making under deep uncertainty",
            "pandemic policy planning",
            "decision_theory",
            ("deep uncertainty", "robust decision making", "adaptive policy"),
            ("decisions can be evaluated without assuming a single reliable predictive model",),
            ("application context is policy planning; robustness is not universal optimality",),
            ("deeply uncertain, non-stationary policy problems",),
            ("RDM", "scenario exploration", "adaptive monitoring"),
            ("robust_decision", "decision_governance", "uncertainty"),
            ("evaluate strategies across plausible futures", "record assumptions and failure conditions"),
            ("prospective policy performance is required",),
            "user-supplied bibliographic block; official PMC landing page",
        ),
        ScientificSourceRecord(
            "dmdu-rand-robust-decision-making",
            "Making Good Decisions Without Predictions: Robust Decision Making for Planning Under Deep Uncertainty",
            (), 2017, "https://www.rand.org/content/dam/rand/pubs/research_briefs/RB9700/RB9701/RAND_RB9701.pdf",
            "https://www.rand.org/content/dam/rand/pubs/research_briefs/RB9700/RB9701/RAND_RB9701.pdf",
            CorpusSourceType.DECISION_THEORY, CorpusEvidenceLevel.METHODOLOGICAL,
            "robust decision making",
            "planning under deep uncertainty",
            "decision_theory",
            ("deep uncertainty", "robustness", "scenario discovery"),
            ("RDM seeks strategies that perform acceptably across many plausible futures",),
            ("robustness criteria depend on decision context and utility thresholds",),
            ("policy and strategic planning under contested models",),
            ("satisficing", "regret", "scenario discovery"),
            ("robust_decision", "scenario_engine", "decision_governance"),
            ("compute performance across explicit uncertainty spaces",),
            ("external outcome validation",),
            "user-supplied bibliographic block; RAND",
        ),
        ScientificSourceRecord(
            "ensemble-bayesian-model-averaging",
            "Improving Predictions using Ensemble Bayesian Model Averaging",
            (), 2013, "https://www.cambridge.org/core/journals/political-analysis/article/improving-predictions-using-ensemble-bayesian-model-averaging/11866974EE2888D4A2988309FC6B602F",
            "https://www.cambridge.org/core/journals/political-analysis/article/improving-predictions-using-ensemble-bayesian-model-averaging/11866974EE2888D4A2988309FC6B602F",
            CorpusSourceType.FORECASTING, CorpusEvidenceLevel.METHODOLOGICAL,
            "ensemble Bayesian model averaging",
            "out-of-sample forecasting",
            "forecasting",
            ("model uncertainty", "forecast aggregation", "out-of-sample validation"),
            ("combining component models can improve out-of-sample forecasts",),
            ("performance depends on validation design and predictive likelihood specification",),
            ("forecasting applications with comparable target variables",),
            ("Bayesian model averaging", "validation-weighted aggregation", "model disagreement"),
            ("forecasting", "model_governance", "calibration"),
            ("aggregate probabilistic forecasts using validation log predictive scores",),
            ("prospective calibration and domain transfer validation",),
            "user-supplied bibliographic block; Cambridge University Press",
        ),
        ScientificSourceRecord(
            "causal-generalizability-bareinboim",
            "Generalizability in Causal Inference: Theory and Algorithms",
            (), 2014, "https://causalai.net/thesis-bareinboim.pdf",
            "https://causalai.net/thesis-bareinboim.pdf",
            CorpusSourceType.CAUSAL_INFERENCE, CorpusEvidenceLevel.METHODOLOGICAL,
            "transportability and generalizability in causal inference",
            "causal effect transport",
            "causal_inference",
            ("identifiability", "transportability", "causal assumptions"),
            ("causal conclusions require explicit identification conditions",),
            ("unobserved confounding and target-population assumptions can remain untestable",),
            ("cross-context causal inference",),
            ("identification", "transportability", "sensitivity analysis"),
            ("causal_governance", "counterfactual_reasoning", "decision_governance"),
            ("persist estimand, assumptions and target population with every causal claim",),
            ("prospective and external validation of transportability",),
            "user-supplied bibliographic block; author-hosted thesis",
        ),
    )
    for record in records:
        try:
            corpus.register(record)
        except ValueError as exc:
            if "already exists" not in str(exc):
                raise

    corpus.add_impact(ScientificImpactMap(
        "impact-dmdu-rdm-v1",
        tuple(record.source_id for record in records[:2]),
        "deep uncertainty",
        "Decision support should remain useful without assuming one correct predictive distribution.",
        "methodological",
        "contested/non-stationary decision environments",
        ("robustness is context-dependent", "plausible futures are not automatically probabilistic"),
        ("exploratory modeling", "satisficing", "regret", "adaptive pathways", "signposts"),
        ("decision_governance", "uncertainty", "response_closure"),
        ("no explicit robust strategy evaluation existed in the current scientific layer",),
        ("enumerate plausible futures", "evaluate strategies without future probabilities", "persist signposts and triggers"),
        ("connect robustness profiles to release/review/abstain", "link signposts to response pathways"),
        ("deterministic scenario enumeration", "worst-case/regret tests", "pathway trigger tests"),
        ("unit-level mathematical validation is possible now",),
        ("prospective strategy performance remains required",),
        ("scenario definition", "client utility/threshold specification"),
        ("mission-rdm-runtime-bridge-v1", "mission-adaptive-pathway-outcome-validation-v1"),
        assumptions=("performance function is decision-relevant", "thresholds are explicit"),
        uncertainty=("future distribution is unknown",),
        identifiability="not a probabilistic identification claim",
        applicability_boundary="decision problems with explicit strategy performance criteria",
    ))
    corpus.add_impact(ScientificImpactMap(
        "impact-ensemble-bma-v1",
        (records[2].source_id,),
        "forecast model uncertainty",
        "Validation-weighted probabilistic model aggregation can reduce dependence on a single selected model.",
        "methodological",
        "targets with comparable probabilistic forecasts and defensible validation sets",
        ("not universal superiority", "validation leakage can invalidate weights", "component model dependence matters"),
        ("Bayesian model averaging", "log predictive scoring", "disagreement quantification"),
        ("forecasting", "calibration", "model_governance"),
        ("no canonical BMA settlement/weighting mechanism",),
        ("compute validation log scores", "derive posterior model weights", "retain ensemble disagreement"),
        ("integrate disagreement into uncertainty governance", "persist validation window and model release hashes"),
        ("posterior-weight normalization", "weight-dominance", "OOS leakage tests"),
        ("closed-form weighting tests are possible now",),
        ("prospective OOS validation remains required",),
        ("model release registry", "point-in-time validation data"),
        ("mission-bma-runtime-bridge-v1", "mission-ensemble-prospective-validation-v1"),
        assumptions=("validation scores are comparable predictive log likelihoods",),
        uncertainty=("model space is incomplete",),
        identifiability="aggregation does not identify the true data-generating model",
        applicability_boundary="probabilistic forecasts sharing a defined target and horizon",
    ))
