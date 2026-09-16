from app.core.scientific.scientific_corpus_install import install_full_scientific_corpus
from app.core.scientific.source_corpus import ScientificSourceCorpus


def test_secondary_received_sources_are_ingested_and_traceable(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    install_full_scientific_corpus(corpus)
    ids = {source.source_id for source in corpus.all_latest()}
    assert "causal-longitudinal-ipw-msm-constraint" in ids
    assert "spatial-csd-2024-constraint" in ids
    assert "performance-incentives-2022-rapid-review" in ids
    assert any(impact.impact_id == "impact-secondary-received-constraints-v1" for impact in corpus.impacts())
    assert corpus.verify_integrity()
