from app.core.scientific.scientific_corpus_install import install_full_scientific_corpus
from app.core.scientific.source_corpus import ScientificSourceCorpus


def test_full_corpus_contains_all_received_scientific_blocks(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    install_full_scientific_corpus(corpus)
    source_ids = {source.source_id for source in corpus.all_latest()}
    required = {
        "sawada-2022-cry-wolf",
        "dakos-2012-csd-robustness",
        "forestal-2020-prediction-markets",
        "forin-2019-ews",
        "bevan-hood-2006-target-gaming",
        "dmdu-rdm-pandemic-2023",
        "wolpert-macready-1997-no-free-lunch",
        "pearl-2009-causality",
        "reference-class-forecasting-constraint",
        "taleb-2007-black-swan",
        "early-warning-impossibility-constraint",
    }
    assert required <= source_ids
    assert corpus.verify_integrity()
    assert any(impact.impact_id == "impact-cross-cutting-epistemic-constraints-v1" for impact in corpus.impacts())
    assert any(mission[1] == "mission-cross-cutting-scientific-runtime-v1" for mission in corpus.missions())
