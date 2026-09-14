from app.core.scientific.source_corpus import (
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


def source(source_id: str, version: int = 1) -> ScientificSourceRecord:
    return ScientificSourceRecord(
        source_id=source_id,
        title=f"Source {source_id}",
        authors=("Author",),
        year=2024,
        identifier=f"doi:{source_id}",
        official_url="https://example.org/source",
        source_type=CorpusSourceType.METHODOLOGICAL,
        evidence_level=CorpusEvidenceLevel.METHODOLOGICAL,
        methodology="comparative methodological study",
        population_context="specified research context",
        domain="complex_systems",
        phenomenon=("regime_change",),
        findings=("signal can change before a transition",),
        limitations=("not universal",),
        applicability=("supporting evidence only",),
        relevant_mechanism=("early_warning",),
        ceutia_components=("governance", "forecasting"),
        implementation_implications=("persist assumptions and limits",),
        validation_requirements=("prospective outcome validation",),
        provenance="peer-reviewed source",
        version=version,
        retrieval=RetrievalMetadata(
            retrieved_at="2026-09-15T00:00:00+00:00",
            retrieval_method="verified_web_retrieval",
            retriever="CeutIA scientific ingestion",
            content_fingerprint="0" * 64,
            canonical_url="https://example.org/source",
        ),
    )


def test_source_versions_are_append_only_and_restartable(tmp_path):
    db = tmp_path / "scientific.sqlite"
    corpus = ScientificSourceCorpus(str(db))
    first = source("s1")
    second = source("s1", version=2)
    corpus.register(first)
    corpus.register(second)

    assert corpus.get("s1").version == 2
    assert corpus.get("s1", 1).record_hash == first.record_hash
    assert len(corpus.all_latest()) == 1
    assert corpus.verify_integrity()

    restored = ScientificSourceCorpus(str(db))
    assert restored.get("s1").record_hash == second.record_hash


def test_duplicate_version_and_tampering_fail_closed(tmp_path):
    db = tmp_path / "scientific.sqlite"
    corpus = ScientificSourceCorpus(str(db))
    corpus.register(source("s1"))
    try:
        corpus.register(source("s1"))
    except ValueError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("duplicate version was accepted")

    with corpus._db() as conn:
        conn.execute("UPDATE scientific_sources SET payload=? WHERE source_id=? AND version=?", ('{"corrupted":true}', "s1", 1))
    assert not corpus.verify_integrity()


def test_relations_impacts_and_missions_persist(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    corpus.register(source("s1"))
    corpus.register(source("s2"))
    corpus.add_relation(ScientificRelation("s1", "s2", ImpactRelation.COMPLEMENTS, "different methods address the same risk"))
    impact = ScientificImpactMap(
        impact_id="impact-1",
        source_ids=("s1", "s2"),
        phenomenon="early-warning fragility",
        supported_claim="signals require context and explicit limits",
        evidence_level="methodological",
        valid_context="time-series monitoring with known sampling assumptions",
        limitations=("observational validity remains open",),
        mechanism=("supporting-signal governance", "bounded uncertainty"),
        existing_components=("early_warning_governance", "scientific_governance"),
        contradictions_or_modifications=("do not treat one indicator as sufficient proof",),
        missing_capabilities=("prospective calibration",),
        implementation_now=("persist source-to-mechanism impact records",),
        integration_requirements=("governance signal", "decision lineage"),
        tests_required=("restart", "tamper detection", "adversarial composition"),
        internal_validation=("hash verification",),
        external_validation=("prospective event outcomes",),
        dependencies=("source provenance",),
        mission_queue=("build prospective early-warning validation harness",),
        assumptions=("source classification is correct",),
        uncertainty=("effect size in CeutIA deployment is unknown",),
        identifiability="descriptive mechanism identifiable; deployment effect not yet identifiable",
        applicability_boundary="do not generalize beyond supported domains",
        validation_status=ValidationStatus.PROSPECTIVE_REQUIRED,
    )
    corpus.add_impact(impact)

    restored = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    assert restored.relations("s1")[0].relation is ImpactRelation.COMPLEMENTS
    assert restored.impacts()[0].impact_hash == impact.impact_hash
    assert restored.missions()[0][1] == "build prospective early-warning validation harness"
    assert restored.verify_integrity()
