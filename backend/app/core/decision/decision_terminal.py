"""Explicit terminal dispositions for every decision path."""
from __future__ import annotations

from enum import StrEnum


class TerminalDisposition(StrEnum):
    DECISION = "decision"
    HUMAN_REVIEW = "human_review"
    ABSTENTION = "abstention"


def validate_terminal(disposition: TerminalDisposition) -> TerminalDisposition:
    if disposition not in TerminalDisposition:
        raise ValueError("invalid terminal disposition")
    return disposition


__all__ = ["TerminalDisposition", "validate_terminal"]
