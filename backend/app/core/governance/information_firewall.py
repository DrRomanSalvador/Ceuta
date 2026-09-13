from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Audience(StrEnum):
    PUBLIC = "PUBLIC"
    OWNER = "OWNER"


@dataclass(frozen=True, slots=True)
class InformationItem:
    item_id: str
    audience: Audience
    content: str
    evidence_ids: tuple[str, ...]


class InformationFirewall:
    def release(self, item: InformationItem, audience: Audience) -> InformationItem:
        if audience == Audience.PUBLIC and item.audience != Audience.PUBLIC:
            raise PermissionError("OWNER information cannot cross the public firewall")
        return item
