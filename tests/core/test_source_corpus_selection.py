from app.core.scientific.initial_corpus import install_current_corpus
from app.core.scientific.source_corpus import CorpusEvidenceLevel, ScientificSourceCorpus


def test_selection_respects_domain_and_minimum_evidence(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    install_current_corpus(corpus)

    disaster = corpus.select(domain="disaster_risk", minimum_evidence_level=CorpusEvidenceLevel.SYSTEMATIC_REVIEW)
    assert disaster
    assert all(source.domain == "disaster_risk" for source in disaster)
    assert all(corpus._LEVEL_RANK[source.evidence_level] >= corpus._LEVEL_RANK[CorpusEvidenceLevel.SYSTEMATIC_REVIEW] for source in disaster)

    forecasting = corpus.select(domain="forecasting", minimum_evidence_level=CorpusEvidenceLevel.META_ANALYTIC)
    assert forecasting
    assert forecasting[0].source_id == "forestal-2020-prediction-markets"


def test_empty_context_fields_do_not_create_false_exclusion(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    install_current_corpus(corpus)
    selected = corpus.select(client="any-client", question_type="any-question", risk_level="high", response_type="decision", context="unknown")
    assert selected
