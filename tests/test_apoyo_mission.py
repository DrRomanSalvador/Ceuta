from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

from app.missions.apoyo import ApoyoError, ApoyoRuntime, CollaborationRequest, ReplicationRequest

ROOT = Path(__file__).resolve().parents[1]
STATE_TEMPLATE = ROOT / "docs" / "missions" / "apoyo" / "APOYO_MISSION_STATE.json"


def runtime(tmp_path: Path) -> ApoyoRuntime:
    state = json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))
    target = tmp_path / "APOYO_MISSION_STATE.json"
    target.write_text(json.dumps(state), encoding="utf-8")
    return ApoyoRuntime(ROOT, state_path=target)


def request(**kwargs) -> CollaborationRequest:
    values = dict(requesting_mission="MISSION-01", request_id="r1", requested_capability="audit", objective="audit x", scope="repo", urgency="normal", constraints=(), expected_output="report", authority={"CAN_INVOKE": True})
    values.update(kwargs)
    return CollaborationRequest(**values)


def test_discovery_and_meeting_point_survive_zero_context(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    assert rt.discover()["meeting_point"]["meeting_point_id"] == "APOYO-MEETING-POINT"
    recovered = rt.recover_role("APOYO")
    assert recovered["identity"]["canonical_name"] == "APOYO"
    assert recovered["meeting_point"]["meeting_point_id"] == "APOYO-MEETING-POINT"
    assert recovered["mission_lifecycle"] == "ACTIVE"


def test_active_agent_keeps_mission_alive_after_task_completion(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="agent-1", mission_id="MISSION-01", account=None, repository="Ceuta", activity="working", state_name="ACTIVE")
    result = rt.final_scan()
    assert result["mission_complete"] is False
    assert rt.load()["mission_lifecycle"] == "ACTIVE"


def test_finished_agent_allows_completion_when_no_work_remains(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="agent-1", mission_id="MISSION-01", account=None, repository="Ceuta", activity="working", state_name="ACTIVE")
    rt.remove_agent_presence("agent-1")
    result = rt.final_scan()
    assert result["mission_complete"] is True
    assert rt.load()["state"] == "RETIRED"


def test_return_command_restores_role(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.load()["state"] = "RETIRED"
    rt.recover_role("return to meeting point")
    assert rt.load()["state"] == "RECOVERING"
    assert rt.load()["mission_lifecycle"] == "ACTIVE"


def test_invocation_preserves_requester_authority_and_returns_control(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    collab = rt.invoke(request())
    assert collab["authority"]["CAN_INVOKE"] is True
    rt.accept("r1")
    rt.validate("r1", evidence_refs=("evidence://1",))
    completed = rt.return_control("r1", result="done", evidence_refs=("evidence://1",))
    assert completed["state"] == "COMPLETED"
    assert "r1" not in rt.load()["active_collaborations"]


def test_unauthorized_invocation_fails_closed(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    with pytest.raises(ApoyoError, match="REQUEST_AUTHORITY_DENIED"):
        rt.invoke(request(authority={"CAN_INVOKE": False}))


def test_unknown_requester_fails_closed(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    with pytest.raises(ApoyoError, match="REQUESTING_MISSION_NOT_DISCOVERABLE"):
        rt.invoke(request(requesting_mission="UNKNOWN"))


def test_duplicate_active_work_returns_no_action(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.invoke(request())
    result = rt.invoke(request(request_id="r2"))
    assert result["status"] == "NO_ACTION"


def test_replication_does_not_fake_a_new_session(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    with pytest.raises(ApoyoError, match="ACCOUNT_AUTHORIZATION"):
        rt.request_replication(ReplicationRequest("MISSION-01", "rep1", "support", "help", "scope", {"CAN_INVOKE": True}))


def test_three_account_policy_fails_closed_when_unconfigured(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    account_path = tmp_path / "accounts.json"
    account_path.write_text(json.dumps({"required_account_count": 3, "authorized_accounts": [], "status": "ACTIVE"}), encoding="utf-8")
    rt.account_path = account_path
    with pytest.raises(ApoyoError, match="ACCOUNT_AUTHORIZATION_INVALID"):
        rt.request_replication(ReplicationRequest("MISSION-01", "rep2", "support", "help", "scope", {"CAN_INVOKE": True}))


def test_stale_writer_is_rejected(tmp_path: Path) -> None:
    first = runtime(tmp_path)
    second = ApoyoRuntime(ROOT, state_path=tmp_path / "APOYO_MISSION_STATE.json")
    state_a = first.load()
    state_b = second.load()
    state_a["events"].append({"type": "writer-a"})
    state_b["events"].append({"type": "writer-b"})
    first._persist(state_a)
    with pytest.raises(ApoyoError, match="STALE_STATE_VERSION"):
        second._persist(state_b)


def test_state_identity_cannot_be_redefined(tmp_path: Path) -> None:
    state_path = tmp_path / "APOYO_MISSION_STATE.json"
    payload = json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))
    payload["mission_id"] = "OTHER"
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    rt = ApoyoRuntime(ROOT, state_path=state_path)
    with pytest.raises(ApoyoError, match="INVALID_APOYO_STATE_IDENTITY"):
        rt.load()


def test_return_command_is_not_a_new_mission(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    state = rt.recover_role("meeting point")
    assert state["mission_id"] == "APOYO"
    assert state["meeting_point"]["meeting_point_id"] == "APOYO-MEETING-POINT"


def test_active_agent_has_priority_over_completion_even_when_no_task_is_assigned(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="agent-2", mission_id="MISSION-02", account=None, repository="Ceuta", activity="analysis", state_name="WORKING")
    assert rt.can_complete()["mission_complete"] is False
    assert rt.can_complete()["active_agents"] == 1


def test_no_artificial_work_allows_completion_after_final_scan(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    result = rt.final_scan()
    assert result["mission_complete"] is True
    assert rt.load()["mission_lifecycle"] == "COMPLETED"
