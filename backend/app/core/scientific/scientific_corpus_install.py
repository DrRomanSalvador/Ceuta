"""Canonical cumulative scientific corpus installer."""
from __future__ import annotations

from .dmdu_corpus import register_dmdu_block
from .epistemic_constraints_corpus import register_epistemic_constraints_block
from .goodhart_corpus import register_goodhart_block
from .initial_corpus import install_current_corpus
from .secondary_received_corpus import register_secondary_received_block
from .source_corpus import ScientificSourceCorpus


def install_full_scientific_corpus(corpus: ScientificSourceCorpus) -> None:
    install_current_corpus(corpus)
    register_dmdu_block(corpus)
    register_goodhart_block(corpus)
    register_epistemic_constraints_block(corpus)
    register_secondary_received_block(corpus)


__all__ = ["install_full_scientific_corpus"]
