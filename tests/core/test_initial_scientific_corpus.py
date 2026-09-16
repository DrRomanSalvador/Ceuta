from app.core.scientific.initial_corpus import current_impacts, current_sources, install_current_corpus
from app.core.scientific.source_corpus import ScientificSourceCorpus, ValidationStatus


def test_current_bibliography_is_structured_and_nonempty(tmp_path):
    sources = current_sources()
    assert len(sources) >= 8
    assert {source.source_type.value for source in sources} >= {
        "systematic_review", "meta_analysis", "methodological", "early_warning", "complex_systems"
    }
    assert all(source.official_url for source in sources)
    assert all(source.identifier for source in sources)
    assert all(source.retrieval is not None for source in sources)
    assert all(len(source.record_hash) == 64 for source in sources)


def test_install_persists_relations_impacts_and_missions(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    install_current_corpus(corpus)

    assert len(corpus.all_latest()) >= 8
    assert corpus.relations("sawada-2022-cry-wolf")
    assert len(corpus.impacts()) == len(current_impacts())
    assert corpus.missions("open")
    assert any(impact.validation_status is ValidationStatus.PROSPECTIVE_REQUIRED for impact in corpus.impacts())
    assert corpus.verify_integrity()


def test_cross_source_map_keeps_contradictions_and_uncertainty(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    install_current_corpus(corpus)
    impact = corpus.impacts()[0]

    assert impact.contradictions_or_modifications
    assert impact.missing_capabilities
    assert impact.external_validation
    assert impact.uncertainty
    assert impact.applicability_boundary
