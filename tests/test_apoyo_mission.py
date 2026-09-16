from __future__ import annotations

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
    values = dict(
        requesting_mission="MISSION-01", request_id="r1", requested_capability="audit",
        objective="audit x", scope="repo", urgency="normal", constraints=(),
        expected_output="report", authority={"CAN_INVOKE": True},
    )
    values.update(kwargs)
    return CollaborationRequest(**values)


def test_01_bootstrap_occupies_empty_meeting_point(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    state = rt.bootstrap()
    assert state["state"] == "WAITING_AT_MEETING_POINT"
    assert state["mission_lifecycle"] == "ACTIVE"
    assert state["meeting_point"]["current_instance"] == "APOYO-ROOT"


def test_02_engineer_arrival_is_detected_and_greeted(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    rt.register_agent_presence(agent_id="engineer-1", mission_id="MISSION-01", account="engineer-account", repository="Ceuta", activity="entering mission", state_name="ENTERING_MISSION")
    assert rt.greet_agent("engineer-1")["status"] == "GREETING_RECORDED"
    assert rt.load()["known_agents"]["engineer-1"]["greeted"] is True


def test_03_support_is_proactively_offered(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    rt.register_agent_presence(agent_id="engineer-1", mission_id="MISSION-01", account=None, repository="Ceuta", activity="working", state_name="WORKING")
    offer = rt.offer_support("engineer-1")
    assert offer["status"] == "SUPPORT_OFFERED"
    assert offer["subordinate"] is True


def test_04_engineer_can_assign_real_support_task(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    rt.register_agent_presence(agent_id="engineer-1", mission_id="MISSION-01", account=None, repository="Ceuta", activity="working", state_name="WORKING")
    task = rt.assign_support_task(agent_id="engineer-1", request_id="eng-task-1", capability="test", objective="run targeted tests", scope="APOYO", authority={"CAN_INVOKE": True})
    assert task["state"] == "ASSIGNED"
    assert rt.load()["active_collaborations"]["eng-task-1"]["requesting_mission"] == "MISSION-01"


def test_05_successor_is_required_without_faking_materialization(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    rt.register_agent_presence(agent_id="engineer-1", mission_id="MISSION-01", account=None, repository="Ceuta", activity="working", state_name="WORKING")
    rt.assign_support_task(agent_id="engineer-1", request_id="eng-task-1", capability="test", objective="run tests", scope="APOYO", authority={"CAN_INVOKE": True})
    successor = rt.ensure_successor(reason="current instance executing engineer task", requesting_mission="MISSION-01", task_request_id="eng-task-1")
    assert successor["status"] == "ACTIVATION_REQUIRED"
    assert successor["materialized"] is False
    assert successor["meeting_point_status"] == "ACTIVATION_REQUIRED"


def test_06_successor_slot_is_single_and_deduplicated(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    first = rt.ensure_successor(reason="coverage required")
    second = rt.ensure_successor(reason="same coverage still required")
    assert first["successor_instance_id"] == second["successor_instance_id"]


def test_07_roman_is_a_supported_principal_actor_and_is_greeted(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    rt.register_agent_presence(agent_id="roman-1", mission_id="ROMÁN", account="principal", repository="Ceuta", activity="direct work", state_name="WORKING")
    assert rt.greet_agent("roman-1")["status"] == "GREETING_RECORDED"
    assert rt.offer_support("roman-1")["status"] == "SUPPORT_OFFERED"


def test_08_roman_can_assign_support_task_and_successor_slot_is_created(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    rt.register_agent_presence(agent_id="roman-1", mission_id="ROMÁN", account="principal", repository="Ceuta", activity="direct work", state_name="WORKING")
    rt.assign_support_task(agent_id="roman-1", request_id="roman-task-1", capability="audit", objective="audit APOYO", scope="APOYO", authority={"CAN_INVOKE": True})
    successor = rt.ensure_successor(reason="preserve reception capacity for next agent", requesting_mission="ROMÁN", task_request_id="roman-task-1")
    assert successor["parent_instance_id"] == "APOYO-ROOT"
    assert successor["requesting_mission"] == "ROMÁN"


def test_09_successive_agents_keep_global_support_active(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    for idx, (agent_id, mission_id) in enumerate((("eng", "MISSION-01"), ("roman", "ROMÁN"), ("eng2", "MISSION-01")), start=1):
        rt.register_agent_presence(agent_id=agent_id, mission_id=mission_id, account=None, repository="Ceuta", activity=f"phase {idx}", state_name="WORKING")
        rt.greet_agent(agent_id)
        rt.offer_support(agent_id)
    assert len(rt.scan_active_agents()["agents"]) == 3
    assert rt.final_scan()["mission_complete"] is False


def test_10_concurrent_meeting_point_claim_does_not_duplicate_live_slot(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    state = rt.load()
    state["instances"]["APOYO-001"] = {
        "instance_id": "APOYO-001", "parent_instance": "APOYO-ROOT", "generation": 1,
        "lineage_id": "APOYO-LINEAGE-ROOT", "state": "WAITING_AT_MEETING_POINT",
        "meeting_point_status": "OCCUPIED", "assigned_scope": None, "current_task": None,
        "memory_checkpoint": None, "collaboration_history": [],
    }
    state["state_version"] = "GENESIS"
    rt._persist(state)
    result = rt.occupy_meeting_point(instance_id="APOYO-001")
    assert result["claimed"] is False
    assert result["reason"] == "MEETING_POINT_ALREADY_OCCUPIED"


def test_11_disappearance_can_be_detected_as_coverage_failure(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    state = rt.load()
    state["meeting_point"]["current_instance"] = "APOYO-MISSING"
    state["events"].append({"type": "MEETING_POINT_COVERAGE_FAILURE", "reason": "INSTANCE_DISAPPEARED"})
    state["state_version"] = "GENESIS"
    rt._persist(state)
    assert any(e["type"] == "MEETING_POINT_COVERAGE_FAILURE" for e in rt.load()["events"])
    successor = rt.ensure_successor(reason="recover missing meeting-point coverage")
    assert successor["status"] == "ACTIVATION_REQUIRED"


def test_12_no_agents_and_no_work_allows_completion(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    result = rt.final_scan()
    assert result["mission_complete"] is True
    assert rt.load()["mission_lifecycle"] == "COMPLETED"


def test_13_pending_task_blocks_completion(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    rt.register_agent_presence(agent_id="engineer-1", mission_id="MISSION-01", account=None, repository="Ceuta", activity="working", state_name="WORKING")
    rt.assign_support_task(agent_id="engineer-1", request_id="pending-1", capability="audit", objective="pending", scope="repo", authority={"CAN_INVOKE": True})
    assert rt.final_scan()["mission_complete"] is False


def test_14_active_agent_blocks_completion_even_without_task(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="agent-2", mission_id="MISSION-02", account=None, repository="Ceuta", activity="analysis", state_name="WORKING")
    assert rt.can_complete()["mission_complete"] is False


def test_15_prospective_agent_blocks_completion(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="incoming", mission_id="MISSION-01", account=None, repository="Ceuta", activity="about to start", state_name="ENTERING_MISSION")
    result = rt.final_scan()
    assert result["mission_complete"] is False
    assert result["prospective_agents"] == 1


def test_16_waiting_is_not_done_when_meeting_point_is_required(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    state = rt.load()
    state["known_agents"]["engineer"] = {"agent_id": "engineer", "mission_id": "MISSION-01", "account": None, "repository": "Ceuta", "activity": "working", "state": "ACTIVE"}
    state["state_version"] = "GENESIS"
    rt._persist(state)
    assert rt.final_scan()["mission_complete"] is False


def test_17_recovery_command_restores_role_and_meeting_point(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    state = rt.recover_role("vuelve al meeting point")
    assert state["mission_id"] == "APOYO"
    assert state["state"] == "WAITING_AT_MEETING_POINT"
    assert state["mission_lifecycle"] == "ACTIVE"
    assert state["meeting_point"]["meeting_point_id"] == "APOYO-MEETING-POINT"


def test_18_external_replication_is_never_fabricated(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    with pytest.raises(ApoyoError, match="ACCOUNT_AUTHORIZATION"):
        rt.request_replication(ReplicationRequest("MISSION-01", "rep1", "support", "help", "scope", {"CAN_INVOKE": True}))


def test_19_three_account_policy_fails_closed_when_unconfigured(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    account_path = tmp_path / "accounts.json"
    account_path.write_text(json.dumps({"required_account_count": 3, "authorized_accounts": [], "status": "ACTIVE"}), encoding="utf-8")
    rt.account_path = account_path
    with pytest.raises(ApoyoError, match="ACCOUNT_AUTHORIZATION_INVALID"):
        rt.request_replication(ReplicationRequest("MISSION-01", "rep2", "support", "help", "scope", {"CAN_INVOKE": True}))


def test_20_stale_writer_is_rejected(tmp_path: Path) -> None:
    first = runtime(tmp_path)
    second = ApoyoRuntime(ROOT, state_path=tmp_path / "APOYO_MISSION_STATE.json")
    state_a = first.load()
    state_b = second.load()
    state_a["events"].append({"type": "writer-a"})
    state_b["events"].append({"type": "writer-b"})
    first._persist(state_a)
    with pytest.raises(ApoyoError, match="STALE_STATE_VERSION"):
        second._persist(state_b)


def test_21_identity_cannot_be_redefined(tmp_path: Path) -> None:
    state_path = tmp_path / "APOYO_MISSION_STATE.json"
    payload = json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))
    payload["mission_id"] = "OTHER"
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    rt = ApoyoRuntime(ROOT, state_path=state_path)
    with pytest.raises(ApoyoError, match="INVALID_APOYO_STATE_IDENTITY"):
        rt.load()


def test_22_collaboration_returns_to_active_support_after_handoff(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.bootstrap()
    collab = rt.invoke(request())
    rt.accept("r1")
    rt.validate("r1", evidence_refs=("evidence://1",))
    completed = rt.return_control("r1", result="done", evidence_refs=("evidence://1",))
    assert completed["state"] == "COMPLETED"
    assert rt.load()["mission_lifecycle"] == "ACTIVE"
    assert "r1" not in rt.load()["active_collaborations"]
    assert any(e["type"] == "SUPPORT_CONTINUES" for e in rt.load()["events"])


def test_23_duplicate_work_returns_no_action(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.invoke(request())
    result = rt.invoke(request(request_id="r2"))
    assert result["status"] == "NO_ACTION"


def test_24_unauthorized_invocation_fails_closed(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    with pytest.raises(ApoyoError, match="REQUEST_AUTHORITY_DENIED"):
        rt.invoke(request(authority={"CAN_INVOKE": False}))


def test_25_unknown_requester_fails_closed(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    with pytest.raises(ApoyoError, match="REQUESTING_MISSION_NOT_DISCOVERABLE"):
        rt.invoke(request(requesting_mission="UNKNOWN"))
