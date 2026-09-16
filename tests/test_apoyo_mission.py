from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.missions.apoyo import ApoyoError, ApoyoRuntime, CollaborationRequest, ReplicationRequest


ROOT = Path(__file__).resolve().parents[1]
STATE_TEMPLATE = ROOT / "docs" / "missions" / "apoyo" / "APOYO_MISSION_STATE.json"


def runtime(tmp_path: Path) -> ApoyoRuntime:
    state_path = tmp_path / "APOYO_MISSION_STATE.json"
    state_path.write_text(STATE_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    return ApoyoRuntime(ROOT, state_path=state_path)


def request(request_id: str = "REQ-001") -> CollaborationRequest:
    return CollaborationRequest(
        requesting_mission="ROMAN",
        request_id=request_id,
        requested_capability="AUDIT",
        objective="Audit a bounded artifact",
        scope="One artifact only",
        urgency="NORMAL",
        constraints=("No ownership transfer",),
        expected_output="Audit findings with evidence",
        authority={"CAN_INVOKE": True},
        capability_gap="Independent audit",
    )


def test_discovery_and_meeting_point_survive_zero_context(tmp_path: Path) -> None:
    runtime_instance = runtime(tmp_path)
    discovered = runtime_instance.discover()
    assert discovered["mission_id"] == "APOYO"
    assert discovered["meeting_point"]["meeting_point_id"] == "APOYO-MEETING-POINT"

    recovered = ApoyoRuntime(ROOT, state_path=tmp_path / "APOYO_MISSION_STATE.json").recover()
    assert recovered["mission_id"] == "APOYO"
    assert recovered["state"] == "WAITING"


def test_invocation_preserves_requester_authority_and_returns_control(tmp_path: Path) -> None:
    runtime_instance = runtime(tmp_path)
    created = runtime_instance.invoke(request())
    assert created["requesting_mission"] == "ROMAN"
    assert created["state"] == "INVOKED"

    runtime_instance.accept("REQ-001")
    runtime_instance.validate("REQ-001", evidence_refs=("evidence:1",))
    completed = runtime_instance.return_control("REQ-001", result="validated finding", evidence_refs=("evidence:1",))

    assert completed["state"] == "COMPLETED"
    assert runtime_instance.load()["state"] == "WAITING"
    assert "REQ-001" in runtime_instance.load()["completed_collaborations"]


def test_unauthorized_invocation_fails_closed(tmp_path: Path) -> None:
    runtime_instance = runtime(tmp_path)
    denied = request()
    denied = CollaborationRequest(**{**denied.__dict__, "authority": {"CAN_INVOKE": False}})
    with pytest.raises(ApoyoError, match="REQUEST_AUTHORITY_DENIED"):
        runtime_instance.invoke(denied)


def test_unknown_requesting_mission_fails_closed(tmp_path: Path) -> None:
    runtime_instance = runtime(tmp_path)
    unknown = CollaborationRequest(**{**request().__dict__, "requesting_mission": "NOT_A_MISSION"})
    with pytest.raises(ApoyoError, match="REQUESTING_MISSION_NOT_DISCOVERABLE"):
        runtime_instance.invoke(unknown)


def test_duplicate_active_work_returns_no_action(tmp_path: Path) -> None:
    runtime_instance = runtime(tmp_path)
    runtime_instance.invoke(request("REQ-001"))
    result = runtime_instance.invoke(request("REQ-002"))
    assert result == {"status": "NO_ACTION", "reason": "DUPLICATE_OR_ALREADY_COVERED"}


def test_replication_does_not_fake_a_new_session(tmp_path: Path) -> None:
    runtime_instance = runtime(tmp_path)
    accounts = tmp_path / "accounts.json"
    accounts.write_text(json.dumps({
        "status": "ACTIVE",
        "required_account_count": 3,
        "authorized_accounts": ["account-A", "account-B", "account-C"],
    }), encoding="utf-8")
    runtime_instance.account_path = accounts

    result = runtime_instance.request_replication(ReplicationRequest(
        requesting_mission="ROMAN",
        request_id="REPL-001",
        requested_capability="TESTING",
        objective="Run independent tests",
        scope="Testing only",
        authority={"CAN_INVOKE": True},
        preferred_account="account-A",
    ))
    assert result["status"] == "REPLICATION_NOT_EXECUTABLE_IN_CURRENT_RUNTIME"
    assert result["instance_id"] not in runtime_instance.load()["instances"]


def test_three_account_policy_fails_closed_when_unconfigured(tmp_path: Path) -> None:
    runtime_instance = runtime(tmp_path)
    with pytest.raises(ApoyoError, match="ACCOUNT_AUTHORIZATION_NOT_CONFIGURED"):
        runtime_instance.request_replication(ReplicationRequest(
            requesting_mission="ROMAN",
            request_id="REPL-002",
            requested_capability="TESTING",
            objective="Run independent tests",
            scope="Testing only",
            authority={"CAN_INVOKE": True},
        ))


def test_state_identity_cannot_be_redefined(tmp_path: Path) -> None:
    state_path = tmp_path / "APOYO_MISSION_STATE.json"
    payload = json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))
    payload["mission_id"] = "ROMAN"
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ApoyoError, match="INVALID_APOYO_STATE_IDENTITY"):
        ApoyoRuntime(ROOT, state_path=state_path).load()
