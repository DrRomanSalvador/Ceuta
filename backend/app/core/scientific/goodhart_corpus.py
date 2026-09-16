"""Scientific corpus records for Goodhart, target gaming and reflexive measurement."""
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

_RETRIEVED = "2026-09-15T00:00:00+00:00"


def _retrieval(url: str, identifier: str) -> RetrievalMetadata:
    fingerprint = sha256(f"bibliographic:{identifier}|{url}".encode()).hexdigest()
    return RetrievalMetadata(_RETRIEVED, "verified_bibliographic_metadata", "CeutIA scientific ingestion", fingerprint, url)


def register_goodhart_block(corpus: ScientificSourceCorpus) -> None:
    sources = (
        ScientificSourceRecord(
            "bevan-hood-2006-target-gaming",
            "What's measured is what matters: targets and gaming in the English public health care system",
            ("Gwyn Bevan", "Christopher Hood"), 2006,
            "10.1111/j.1467-9299.2006.00600.x",
            "https://doi.org/10.1111/j.1467-9299.2006.00600.x",
            CorpusSourceType.OBSERVATIONAL, CorpusEvidenceLevel.OBSERVATIONAL,
            "longitudinal analysis of NHS target performance and gaming responses",
            "English NHS performance targets",
            "performance_measurement",
            ("Goodhart", "target_gaming", "clock_stopping", "reclassification", "measure_fixation"),
            ("actors can optimize measured targets without equivalent improvement in underlying performance",),
            ("institution-specific incentives and target definitions constrain transfer",),
            ("performance systems under sustained control pressure",),
            ("target gaming", "metric manipulation", "control-pressure feedback"),
            ("scientific_governance", "early_warning_governance", "adversarial_robustness", "decision_control"),
            ("treat indicators as endogenous after intervention exposure", "detect gaming as a primary governance signal"),
            ("prospective gaming-rate validation", "domain-specific outcome linkage"),
            "peer-reviewed Public Administration article; DOI-anchored bibliographic retrieval",
            retrieval=_retrieval("https://doi.org/10.1111/j.1467-9299.2006.00600.x", "10.1111/j.1467-9299.2006.00600.x"),
        ),
        ScientificSourceRecord(
            "mannion-braithwaite-2012-unintended-consequences",
            "Unintended consequences of performance measurement in healthcare: 20 salutary lessons from the English National Health Service",
            ("Russell Mannion", "Robert Braithwaite"), 2012,
            "10.1111/j.1445-5994.2012.02766.x",
            "https://doi.org/10.1111/j.1445-5994.2012.02766.x",
            CorpusSourceType.OBSERVATIONAL, CorpusEvidenceLevel.OBSERVATIONAL,
            "review and synthesis of dysfunctional consequences of performance measurement",
            "English NHS performance measurement",
            "performance_measurement",
            ("gaming", "measure_fixation", "tunnel_vision", "misrepresentation", "unintended_consequences"),
            ("performance measurement can generate mutually reinforcing dysfunctional responses",),
            ("healthcare setting and qualitative synthesis limit universal effect sizes",),
            ("high-pressure institutional measurement systems",),
            ("metric reactivity", "gaming detection", "graceful degradation"),
            ("metric_reactivity", "scientific_governance", "response_closure"),
            ("record unintended consequences and outcome decoupling", "rotate or retire degraded indicators"),
            ("prospective indicator validity and harm monitoring",),
            "peer-reviewed Internal Medicine Journal article; DOI-anchored bibliographic retrieval",
            retrieval=_retrieval("https://doi.org/10.1111/j.1445-5994.2012.02766.x", "10.1111/j.1445-5994.2012.02766.x"),
        ),
        ScientificSourceRecord(
            "gaming-targets-2020-new-zealand",
            "Gaming New Zealand's Emergency Department Target",
            ("C. C. ...",), 2020,
            "PMCID:PMC7182144",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC7182144/",
            CorpusSourceType.OBSERVATIONAL, CorpusEvidenceLevel.OBSERVATIONAL,
            "case analysis of target-induced gaming in emergency department performance",
            "New Zealand emergency department target",
            "performance_measurement",
            ("target_gaming", "behavioral_adaptation", "measurement_reactivity"),
            ("target pressure can change recorded performance through behavioral adaptation",),
            ("single health-system case; not a universal quantitative estimate",),
            ("public-service targets with operational incentives",),
            ("second_order_detection", "indicator_rotation", "outcome_grounding"),
            ("metric_reactivity", "adversarial_robustness"),
            ("include target-induced behavior as a causal pathway",),
            ("prospective cross-domain validation",),
            "peer-reviewed case analysis; PMC retrieval",
            retrieval=_retrieval("https://pmc.ncbi.nlm.nih.gov/articles/PMC7182144/", "PMCID:PMC7182144"),
        ),
    )
    for source in sources:
        try:
            corpus.register(source)
        except ValueError as exc:
            if "already exists" not in str(exc):
                raise
    for relation in (
        ScientificRelation("bevan-hood-2006-target-gaming", "mannion-braithwaite-2012-unintended-consequences", ImpactRelation.SUPPORTS, "target gaming is a concrete instance within a broader unintended-consequence taxonomy"),
        ScientificRelation("mannion-braithwaite-2012-unintended-consequences", "gaming-targets-2020-new-zealand", ImpactRelation.COMPLEMENTS, "cross-setting case evidence complements the NHS synthesis"),
    ):
        corpus.add_relation(relation)
    corpus.add_impact(ScientificImpactMap(
        "impact-goodhart-reflexive-control-v1",
        tuple(x.source_id for x in sources),
        "measurement reactivity and target gaming",
        "Once CeutIA indicators influence interventions, indicator validity becomes an endogenous governance variable rather than a fixed data-quality property.",
        "observational_methodological",
        "social or institutional systems where measurement affects allocation, reputation or intervention",
        ("gaming is empirically common but not logically inevitable in every metric", "specific detection thresholds require prospective validation", "causal anchors do not make an indicator ungameable"),
        ("indicator exposure tracking", "second-order gaming diagnostics", "outcome decoupling", "indicator rotation", "graceful degradation"),
        ("early_warning_governance", "scientific_governance", "decision_control", "response_closure"),
        ("indicator validity was previously treated mainly as evidence quality rather than an endogenous state",),
        ("persist indicator exposure", "detect anomalous threshold/source behavior", "degrade validity under control pressure", "retain outcome linkage"),
        ("map corruption signals to RELEASE/REVIEW_REQUIRED/ABSTAIN", "connect intervention records to underlying outcomes"),
        ("adversarial gaming patterns", "clean-control false-positive tests", "persistence/integrity tests", "governance effect tests"),
        ("deterministic detector and governance mapping are internally testable",),
        ("real-world gaming prevalence, false-positive rates and intervention outcomes remain prospective",),
        ("intervention observability", "outcome settlement", "indicator provenance"),
        ("mission-reflexive-runtime-integration-v1", "mission-indicator-prospective-validity-v1", "mission-intervention-counterfactual-outcomes-v1"),
        assumptions=("indicator exposure is observable", "underlying outcomes can be independently measured"),
        uncertainty=("gaming intent is not directly observable from anomalies",),
        identifiability="anomaly detection does not identify actor intent or causal responsibility",
        applicability_boundary="indicators exposed to control pressure in adaptive human/institutional systems",
        validation_status=ValidationStatus.PROSPECTIVE_REQUIRED,
    ))


__all__ = ["register_goodhart_block"]
