from app.core.scientific.scientific_corpus_install import install_full_scientific_corpus
from app.core.scientific.source_corpus import ScientificSourceCorpus


def test_installed_scientific_corpus_records_have_operational_consequences(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    install_full_scientific_corpus(corpus)
    sources = corpus.all_latest()
    assert sources
    assert corpus.verify_integrity()
    for source in sources:
        assert source.phenomenon
        assert source.findings
        assert source.limitations
        assert source.applicability
        assert source.relevant_mechanism
        assert source.ceutia_components
        assert source.implementation_implications
        assert source.validation_requirements
