from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from .evolution import AdmissionDecision, EvolutionError, MissionEvolutionEngine

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


class EvolutionRuntimeError(RuntimeError):
    """Raised when an evolution transaction cannot be safely committed."""


class MissionEvolutionRuntime:
    """Persistent, compare-and-swap admission runtime for the mission control plane."""

    def __init__(self, repository_root: Path | str) -> None:
        self.root = Path(repository_root).resolve()
        self.missions_root = self.root / "docs" / "missions"
        self.transactions_root = self.missions_root / "evolution" / "transactions"
        self.transactions_root.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.missions_root / "MISSION_REGISTRY.json"
        self.version_path = self.missions_root / "MISSION_REGISTRY.VERSION"
        self.lock_path = self.missions_root / ".MISSION_REGISTRY.lock"

    def read_registry(self) -> tuple[dict[str, Any], str]:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        return registry, self._registry_version(registry)

    def stage_admission(self, decision: AdmissionDecision, authority_context: Mapping[str, bool]) -> Path:
        if not decision.admitted or decision.proposal is None:
            raise EvolutionRuntimeError("Only an admitted proposal can be staged")
        MissionEvolutionEngine.authorize(decision, authority_context)
        with self._registry_lock():
            registry, base_version = self.read_registry()
            proposal = decision.proposal
            self._assert_absent(registry, proposal.proposed_mission_id)
            path = self.transactions_root / f"{proposal.proposal_id}.json"
            if path.exists():
                raise EvolutionRuntimeError(f"ADMISSION_TRANSACTION_ALREADY_EXISTS: {proposal.proposal_id}")
            self._atomic_write_json(path, self._build_transaction(decision, base_version))
            return path

    def commit_staged(self, proposal_id: str, authority_context: Mapping[str, bool]) -> dict[str, Any]:
        if not authority_context.get("CAN_AUTHORIZE", False):
            raise EvolutionError("Mission admission requires CAN_AUTHORIZE")
        path = self.transactions_root / f"{proposal_id}.json"
        if not path.exists():
            raise EvolutionRuntimeError(f"Admission transaction not found: {proposal_id}")

        with self._registry_lock():
            transaction = json.loads(path.read_text(encoding="utf-8"))
            if transaction.get("status") != "STAGED":
                raise EvolutionRuntimeError("Admission transaction is not committable")
            registry, current_version = self.read_registry()
            if current_version != transaction["base_registry_version"]:
                raise EvolutionRuntimeError("STALE_REGISTRY_VERSION: admission transaction rejected")
            mission_id = transaction["proposal"]["proposed_mission_id"]
            self._assert_absent(registry, mission_id)
            mission_dir = self.missions_root / mission_id.lower()
            if mission_dir.exists():
                raise EvolutionRuntimeError(f"MISSION_ARTIFACT_DIRECTORY_ALREADY_EXISTS: {mission_id}")

            registry["missions"].append(transaction["registration"])
            new_version = self._next_version(current_version)
            self._atomic_write_json(self.registry_path, registry)
            self.version_path.write_text(new_version, encoding="utf-8")
            mission_dir.mkdir(parents=False, exist_ok=False)
            self._atomic_write_json(mission_dir / "INVOCATION_CONTRACT.json", transaction["contract"])
            self._atomic_write_json(mission_dir / "MISSION_STATE.json", {
                "mission_id": mission_id,
                "status": "REGISTERED_PENDING_VALIDATION",
                "registry_version": new_version,
                "current_task": None,
                "next_authorized_action": "ZERO_CONTEXT_DISCOVERY_TEST",
                "provenance_required": True,
            })
            (mission_dir / "CANONICAL_MISSION_PROMPT.md").write_text(transaction["canonical_prompt"], encoding="utf-8")
            self._atomic_write_json(mission_dir / "ADMISSION_PROPOSAL.json", transaction["proposal"])
            transaction["status"] = "COMMITTED"
            transaction["committed_registry_version"] = new_version
            self._atomic_write_json(path, transaction)
            return transaction

    def validate_zero_context(self, mission_id: str) -> dict[str, Any]:
        registry, version = self.read_registry()
        mission = next((m for m in registry.get("missions", []) if m.get("mission_id") == mission_id), None)
        if mission is None:
            return {"passed": False, "reason": "MISSION_NOT_DISCOVERABLE"}
        required = ("canonical_name", "purpose", "invocation_contract", "state_location", "status", "operations", "bootstrap")
        missing = [field for field in required if not mission.get(field)]
        contract_path = self.root / mission.get("invocation_contract", "")
        state_path = self.root / mission.get("state_location", "")
        passed = not missing and contract_path.exists() and state_path.exists()
        return {
            "passed": passed,
            "mission_id": mission_id,
            "registry_version": version,
            "missing": missing,
            "contract_exists": contract_path.exists(),
            "state_exists": state_path.exists(),
            "next": "LOAD_CONTRACT → CHECK_AUTHORITY → CHECK_INPUTS → INVOKE" if passed else "REPAIR_INTEGRATION",
        }

    @staticmethod
    def _build_transaction(decision: AdmissionDecision, base_version: str) -> dict[str, Any]:
        proposal = decision.proposal
        assert proposal is not None
        contract = MissionEvolutionEngine.generate_contract(proposal)
        return {
            "schema_version": "1.0",
            "transaction_type": "MISSION_ADMISSION",
            "status": "STAGED",
            "proposal_id": proposal.proposal_id,
            "base_registry_version": base_version,
            "decision": decision.decision,
            "precedence_path": list(decision.precedence_path),
            "proposal": proposal.as_dict(),
            "contract": contract,
            "registration": MissionEvolutionEngine.generate_registration_entry(proposal),
            "canonical_prompt": MissionEvolutionEngine.generate_canonical_prompt(proposal),
        }

    @staticmethod
    def _assert_absent(registry: Mapping[str, Any], mission_id: str) -> None:
        if any(m.get("mission_id") == mission_id for m in registry.get("missions", [])):
            raise EvolutionRuntimeError(f"MISSION_ALREADY_EXISTS: {mission_id}")

    def _registry_version(self, registry: Mapping[str, Any]) -> str:
        if self.version_path.exists():
            return self.version_path.read_text(encoding="utf-8").strip()
        payload = json.dumps(registry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _next_version(version: str) -> str:
        return hashlib.sha256((version + ":next").encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(value, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    @contextmanager
    def _registry_lock(self) -> Iterator[None]:
        if fcntl is None:
            raise EvolutionRuntimeError("CONCURRENCY_UNSUPPORTED: POSIX file locking is required")
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
