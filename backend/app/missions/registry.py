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

    A host/orchestrator owns live execution, leases, transactions and external
    process supervision. Universal execution policy is composed into every
    loaded mission contract so a mission cannot opt out locally.
    """

    COMMON_REQUIRED_FIELDS = {"mission_id", "canonical_name", "mission_type", "status"}
    UNIVERSAL_CONTRACT = "docs/missions/UNIVERSAL_EXECUTION_CONTRACT.json"

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
        return [dict(mission) for mission in missions if mission["mission_id"].casefold() == needle or mission["canonical_name"].casefold() == needle]

    def get(self, mission_id: str) -> dict[str, Any]:
        matches = self.discover(mission_id)
        if len(matches) != 1:
            raise MissionRegistryError(f"Mission not uniquely discoverable: {mission_id}")
        return matches[0]

    def get_control_plane_capability(self, capability_id: str) -> dict[str, Any]:
        capability = self.load().get("control_plane_capabilities", {}).get(capability_id)
        if not isinstance(capability, dict):
            raise MissionRegistryError(f"Control-plane capability is not registered: {capability_id}")
        return dict(capability)

    def load_contract(self, mission_id: str) -> dict[str, Any]:
        mission = self.get(mission_id)
        contract_ref = mission.get("invocation_contract")
        if not contract_ref:
            raise MissionRegistryError(f"Mission has no machine-readable invocation contract: {mission_id}")
        contract = self._load_json(self.repository_root / contract_ref, f"Cannot load invocation contract: {contract_ref}")
        if contract.get("mission_id") != mission_id:
            raise MissionRegistryError("Mission/contract identity mismatch")
        universal = self._load_json(self.repository_root / self.UNIVERSAL_CONTRACT, "Cannot load universal execution contract")
        contract["universal_execution_contract"] = universal
        contract["execution_inheritance"] = "MANDATORY"
        contract["non_weakening"] = True
        return contract

    def build_invocation(self, *, mission_id: str, operation: str, request_id: str, session_id: str, requested_at: str, authority_context: dict[str, bool], input_refs: tuple[str, ...], expected_output_type: str, base_state_version: str) -> InvocationEnvelope:
        contract = self.load_contract(mission_id)
        operation_upper = operation.upper()
        if operation_upper not in contract.get("operations", []):
            raise MissionRegistryError(f"Unsupported operation for {mission_id}: {operation}")
        if not authority_context.get("CAN_INVOKE", False):
            raise MissionRegistryError("Invocation denied: CAN_INVOKE is not granted")
        return InvocationEnvelope(mission_id, operation_upper, request_id, session_id, requested_at, dict(authority_context), tuple(input_refs), expected_output_type, base_state_version)

    @staticmethod
    def _load_json(path: Path, error_message: str) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MissionRegistryError(error_message) from exc
        if not isinstance(value, dict):
            raise MissionRegistryError(f"Expected JSON object: {path}")
        return value

    @classmethod
    def _validate_registry(cls, registry: dict[str, Any]) -> None:
        missions = registry.get("missions")
        if not isinstance(missions, list) or not missions:
            raise MissionRegistryError("Mission registry contains no missions")
        ids: set[str] = set()
        for mission in missions:
            if not isinstance(mission, dict) or not cls.COMMON_REQUIRED_FIELDS.issubset(mission):
                raise MissionRegistryError("Mission registry entry is missing common required fields")
            mission_id = mission["mission_id"]
            if not isinstance(mission_id, str) or mission_id in ids:
                raise MissionRegistryError("Mission IDs must be unique strings")
            ids.add(mission_id)
        capabilities = registry.get("control_plane_capabilities")
        if not isinstance(capabilities, dict) or "MISSION_EVOLUTION_ENGINE" not in capabilities:
            raise MissionRegistryError("Mission Evolution Engine is not registered as a control-plane capability")
        roman = next((m for m in missions if m.get("mission_id") == "ROMAN"), None)
        if roman is None:
            raise MissionRegistryError("ROMAN is not registered")
        for field in ("invocation_contract", "state_location", "bootstrap", "adversarial_tests"):
            if not roman.get(field):
                raise MissionRegistryError(f"ROMAN missing required integration field: {field}")
        if roman.get("canonical_name") != "ROMÁN":
            raise MissionRegistryError("ROMAN canonical identity is invalid")
        if roman.get("mission_type") != "AUTHORIAL_INTELLECTUAL_FORENSIC":
            raise MissionRegistryError("ROMAN mission type is invalid")
        universal_path = Path(cls.UNIVERSAL_CONTRACT)
        if not universal_path.as_posix().endswith("UNIVERSAL_EXECUTION_CONTRACT.json"):
            raise MissionRegistryError("Universal execution contract reference is invalid")
