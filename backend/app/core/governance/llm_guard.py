from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GuardedPrompt:
    system_instructions: str
    user_content: str
    evidence_ids: tuple[str, ...]


class LLMGuard:
    """LLMs may transform evidence but cannot mutate canonical state or governance controls."""
    def build(self, *, user_content: str, evidence_ids: tuple[str, ...], system_instructions: str) -> GuardedPrompt:
        if not evidence_ids:
            raise PermissionError("LLM analysis requires explicit evidence identifiers")
        return GuardedPrompt(system_instructions, user_content, evidence_ids)

    @staticmethod
    def can_mutate_state() -> bool:
        return False
