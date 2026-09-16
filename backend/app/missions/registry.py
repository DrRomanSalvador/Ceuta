from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


class MissionRegistryError(ValueError):
    """Raised when the canonical mission registry cannot be safely consumed."""


@dataclass(frozen=True, slots=True)
class InvocationEnvelope:
    mission_id: str
    operation: str
    request_id: str
    session_id: str
    requested_at: str
    authority_context: dict[str, bool]
    input_refs: tuple[str, ...]
    expected_output_type: str
    base_state_version: str


class MissionRegistry:
    """Read-only discovery boundary for the canonical multi-mission registry.

    This component deliberately does not mutate mission state or execute intellectual
    work. A host/orchestrator owns execution, leases, transactions and persistence.
    """

    REQUIRED_FIELDS = {
        "mission_id",
        "canonical_name",
        "mission_type",
        "status",
        "invocation_contract",
        "state_location",
    }

    def __init__(self, repository_root: Path | str) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.registry_path = self.repository_root / "docs" / "missions" / "MISSION_REGISTRY.json"
        self._registry: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        if self._registry is None:
            try:
                self._registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise MissionRegistryError(f"Cannot load mission registry: {self.registry_path}") from exc
        self._validate_registry(self._registry)
        return self._registry

    def discover(self, mission_id_or_name: str | None = None) -> list[dict[str, Any]]:
        missions = self.load()["missions"]
        if mission_id_or_name is None:
            return [dict(mission) for mission in missions]
        needle = mission_id_or_name.casefold()
        return [
            dict(mission)
            for mission in missions
            if mission["mission_id"].casefold() == needle
            or mission["canonical_name"].casefold() == needle
        ]

    def get(self, mission_id: str) -> dict[str, Any]:
        matches = self.discover(mission_id)
        if len(matches) != 1:
            raise MissionRegistryError(f"Mission not uniquely discoverable: {mission_id}")
        return matches[0]

    def load_contract(self, mission_id: str) -> dict[str, Any]:
        mission = self.get(mission_id)
        contract_path = self.repository_root / mission["invocation_contract"]
        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MissionRegistryError(f"Cannot load invocation contract: {contract_path}") from exc
        if contract.get("mission_id") != mission_id:
            raise MissionRegistryError("Mission/contract identity mismatch")
        return contract

    def build_invocation(
        self,
        *,
        mission_id: str,
        operation: str,
        request_id: str,
        session_id: str,
        requested_at: str,
        authority_context: dict[str, bool],
        input_refs: tuple[str, ...],
        expected_output_type: str,
        base_state_version: str,
    ) -> InvocationEnvelope:
        contract = self.load_contract(mission_id)
        operation_upper = operation.upper()
        if operation_upper not in contract.get("operations", []):
            raise MissionRegistryError(f"Unsupported operation for {mission_id}: {operation}")
        if not authority_context.get("CAN_INVOKE", False):
            raise MissionRegistryError("Invocation denied: CAN_INVOKE is not granted")
        return InvocationEnvelope(
            mission_id=mission_id,
            operation=operation_upper,
            request_id=request_id,
            session_id=session_id,
            requested_at=requested_at,
            authority_context=dict(authority_context),
            input_refs=tuple(input_refs),
            expected_output_type=expected_output_type,
            base_state_version=base_state_version,
        )

    @classmethod
    def _validate_registry(cls, registry: dict[str, Any]) -> None:
        missions = registry.get("missions")
        if not isinstance(missions, list) or not missions:
            raise MissionRegistryError("Mission registry contains no missions")
        ids: set[str] = set()
        for mission in missions:
            if not isinstance(mission, dict) or not cls.REQUIRED_FIELDS.issubset(mission):
                raise MissionRegistryError("Mission registry entry is missing required fields")
            mission_id = mission["mission_id"]
            if not isinstance(mission_id, str) or mission_id in ids:
                raise MissionRegistryError("Mission IDs must be unique strings")
            ids.add(mission_id)
        roman = next((m for m in missions if m.get("mission_id") == "ROMAN"), None)
        if roman is None:
            raise MissionRegistryError("ROMAN is not registered")
        if roman.get("canonical_name") != "ROMÁN":
            raise MissionRegistryError("ROMAN canonical identity is invalid")
        if roman.get("mission_type") != "AUTHORIAL_INTELLECTUAL_FORENSIC":
            raise MissionRegistryError("ROMAN mission type is invalid")
