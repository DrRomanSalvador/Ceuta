"""Canonical cumulative scientific corpus installer.

Keeps the earlier seed installer unchanged while providing an explicit full
installation surface that composes every received scientific block.
"""
from __future__ import annotations

from .dmdu_corpus import register_dmdu_block
from .goodhart_corpus import register_goodhart_block
from .initial_corpus import install_current_corpus
from .source_corpus import ScientificSourceCorpus


def install_full_scientific_corpus(corpus: ScientificSourceCorpus) -> None:
    install_current_corpus(corpus)
    register_dmdu_block(corpus)
    register_goodhart_block(corpus)


__all__ = ["install_full_scientific_corpus"]
