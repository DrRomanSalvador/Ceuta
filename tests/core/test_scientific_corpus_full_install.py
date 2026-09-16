from app.core.scientific.scientific_corpus_install import install_full_scientific_corpus
from app.core.scientific.source_corpus import ScientificSourceCorpus


def test_full_corpus_contains_goodhart_and_dmdu(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "corpus.sqlite"))
    install_full_scientific_corpus(corpus)
    ids = {source.source_id for source in corpus.all_latest()}
    assert "bevan-hood-2006-target-gaming" in ids
    assert "dmdu-rand-robust-decision-making" in ids
    assert any(impact.impact_id == "impact-goodhart-reflexive-control-v1" for impact in corpus.impacts())
    assert corpus.verify_integrity()
