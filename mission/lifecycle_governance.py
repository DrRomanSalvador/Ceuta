"""Persistent mission admission, retirement, recovery and conflict governance."""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .shared_standard import require_fields

OPERATING_STANDARD_VERSION = "MISSION_SYSTEM_CONSTITUTION_1.0"


def load_ledger(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("admissions", "retirements", "recoveries", "conflicts"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"Lifecycle ledger field {key} must be a list")
    return data


def _write(path: Path, data: dict[str, Any]) -> None:
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise


def admit(path: Path, contract: dict[str, Any], *, authorized_by: str, evidence: list[str]) -> dict[str, Any]:
    required=("mission_id","mission_name","purpose","scope","authority","owner","inputs","outputs","dependencies","handoff_contract","validation_contract","recovery_policy","retirement_conditions","operating_standard_version")
    require_fields(contract, required, "mission admission")
    if not evidence or not authorized_by:
        raise ValueError("Admission requires evidence and authorizer")
    mission_id = contract["mission_id"]
    if not (mission_id.startswith("MISSION-") or mission_id == "ROMAN"):
        raise ValueError("Operational mission IDs must use MISSION-* or the canonical ROMAN namespace")
    if contract["operating_standard_version"] != OPERATING_STANDARD_VERSION:
        raise ValueError("Mission must explicitly inherit the canonical operating standard")
    data=load_ledger(path)
    if any(x["mission_id"]==mission_id and x["status"] in {"ADMITTED","ADMITTED_REPOSITORY_RUNTIME_PENDING"} for x in data["admissions"]):
        raise ValueError("Mission is already admitted")
    status = "ADMITTED_REPOSITORY_RUNTIME_PENDING" if mission_id == "ROMAN" else "ADMITTED"
    record={"mission_id":mission_id,"status":status,"contract":contract,"authorized_by":authorized_by,"evidence":evidence}
    data["admissions"].append(record); _write(path,data); return record


def retire(path: Path, *, mission_id: str, owner: str, authorized_by: str, evidence: list[str], reason: str) -> dict[str, Any]:
    if not all((mission_id, owner, authorized_by, reason)) or not evidence:
        raise ValueError("Retirement requires owner, authorizer, reason and evidence")
    if owner != mission_id:
        raise PermissionError("Only the owning mission may propose retirement")
    data=load_ledger(path)
    record={"mission_id":mission_id,"status":"RETIRED","authorized_by":authorized_by,"evidence":evidence,"reason":reason}
    data["retirements"].append(record); _write(path,data); return record


def recover(path: Path, *, mission_id: str, trigger: str, evidence: list[str], restored_state: str) -> dict[str, Any]:
    require_fields({"mission_id":mission_id,"trigger":trigger,"restored_state":restored_state}, ("mission_id","trigger","restored_state"), "recovery")
    if not evidence: raise ValueError("Recovery requires evidence")
    data=load_ledger(path)
    record={"mission_id":mission_id,"trigger":trigger,"evidence":evidence,"restored_state":restored_state,"status":"RECOVERED"}
    data["recoveries"].append(record); _write(path,data); return record


def record_conflict(path: Path, *, conflict_id: str, claim_a: str, claim_b: str, category: str, owner: str, evidence_a: list[str], evidence_b: list[str]) -> dict[str, Any]:
    if claim_a == claim_b: raise ValueError("Conflict requires distinct claims")
    if not evidence_a or not evidence_b: raise ValueError("Conflict requires evidence for both claims")
    data=load_ledger(path)
    record={"conflict_id":conflict_id,"claim_a":claim_a,"claim_b":claim_b,"category":category,"owner":owner,"evidence_a":evidence_a,"evidence_b":evidence_b,"status":"OPEN"}
    data["conflicts"].append(record); _write(path,data); return record
