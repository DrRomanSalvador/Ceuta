from app.core.scientific.dmdu_corpus import register_dmdu_block
from app.core.scientific.source_corpus import ScientificSourceCorpus


def test_dmdu_block_is_persistent_and_generates_missions(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    register_dmdu_block(corpus)
    assert corpus.verify_integrity()
    sources = corpus.all_latest()
    assert {s.source_id for s in sources} >= {
        "dmdu-rdm-pandemic-2023",
        "dmdu-rand-robust-decision-making",
        "ensemble-bayesian-model-averaging",
        "causal-generalizability-bareinboim",
    }
    impacts = corpus.impacts()
    assert {impact.impact_id for impact in impacts} >= {"impact-dmdu-rdm-v1", "impact-ensemble-bma-v1"}
    assert any("mission-rdm-runtime-bridge-v1" in mission[1] for mission in corpus.missions())


def test_source_selection_respects_minimum_evidence_level(tmp_path):
    corpus = ScientificSourceCorpus(str(tmp_path / "scientific.sqlite"))
    register_dmdu_block(corpus)
    selected = corpus.select(domain="decision_theory")
    assert selected
    assert all(source.domain == "decision_theory" for source in selected)
