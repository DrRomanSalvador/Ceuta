from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.missions.apoyo import ApoyoError, ApoyoRuntime
from app.missions.apoyo_protocol import (
    APOYO_REPLICATION_REQUIREMENT,
    INGENIERO_MISSION_ID,
    INGENIERO_NAME,
    MEETING_POINT_COVERAGE_REQUIRED,
    MEETING_POINT_ID,
    MINIMUM_READY_SUPPORT_INSTANCES,
    assign_support_task,
    completion_blocked_by_agents,
    greeting_window,
    successor_exit_allowed,
)

ROOT = Path(__file__).resolve().parents[1]
STATE_TEMPLATE = ROOT / "docs/missions/apoyo/APOYO_MISSION_STATE.json"


def runtime(tmp_path: Path) -> ApoyoRuntime:
    state = json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))
    target = tmp_path / "APOYO_MISSION_STATE.json"
    target.write_text(json.dumps(state), encoding="utf-8")
    return ApoyoRuntime(ROOT, state_path=target)


def test_apoyo_discovers_ingeniero(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="ingeniero-1", mission_id=INGENIERO_MISSION_ID, account="UNVERIFIED", repository="DrRomanSalvador/Ceuta", activity="testing", state_name="CHECKPOINT")
    agent = rt.scan_active_agents()["agents"][0]
    assert agent["mission_id"] == INGENIERO_MISSION_ID
    assert agent["agent_id"] == "ingeniero-1"
    assert INGENIERO_NAME == "INGENIERO"


def test_apoyo_identifies_repository(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="ingeniero-1", mission_id=INGENIERO_MISSION_ID, account=None, repository="DrRomanSalvador/Ceuta", activity="analysis", state_name="WORKING")
    assert rt.scan_active_agents()["agents"][0]["repository"] == "DrRomanSalvador/Ceuta"


def test_apoyo_identifies_authorized_account_without_assuming_it(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="ingeniero-1", mission_id=INGENIERO_MISSION_ID, account=None, repository="DrRomanSalvador/Ceuta", activity="analysis", state_name="WORKING")
    assert rt.scan_active_agents()["agents"][0]["account"] is None


def test_apoyo_greets_ingeniero_only_in_non_intrusive_window() -> None:
    assert greeting_window("checkpoint", "CHECKPOINT").allowed is True
    assert greeting_window("testing", "TESTING").allowed is False


def test_apoyo_does_not_interrupt_active_execution() -> None:
    decision = greeting_window("debugging", "RUNNING")
    assert decision.allowed is False
    assert decision.reason == "OCCUPIED_AGENT"


def test_apoyo_returns_to_meeting_point() -> None:
    assert MEETING_POINT_ID == "APOYO-MEETING-POINT"


def test_apoyo_remains_active_after_greeting(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="ingeniero-1", mission_id=INGENIERO_MISSION_ID, account=None, repository="DrRomanSalvador/Ceuta", activity="checkpoint", state_name="CHECKPOINT")
    result = rt.final_scan()
    assert result["mission_complete"] is False
    assert rt.load()["mission_lifecycle"] == "ACTIVE"


def test_apoyo_detects_roman(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="roman-1", mission_id="ROMAN", account=None, repository="DrRomanSalvador/Ceuta", activity="working", state_name="ACTIVE")
    assert rt.scan_active_agents()["agents"][0]["mission_id"] == "ROMAN"


def test_apoyo_remains_active_while_roman_is_active(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="roman-1", mission_id="ROMAN", account=None, repository="DrRomanSalvador/Ceuta", activity="working", state_name="ACTIVE")
    assert completion_blocked_by_agents(rt.scan_active_agents()["agents"]) is True
    assert rt.final_scan()["mission_complete"] is False


def test_apoyo_accepts_support_request(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    from app.missions.apoyo import CollaborationRequest
    req = CollaborationRequest("MISSION-01", "support-1", "audit", "help", "repo", "normal", (), "result", {"CAN_INVOKE": True})
    assert rt.invoke(req)["request_id"] == "support-1"


def test_apoyo_returns_control(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    from app.missions.apoyo import CollaborationRequest
    req = CollaborationRequest("MISSION-01", "support-2", "audit", "help", "repo", "normal", (), "result", {"CAN_INVOKE": True})
    rt.invoke(req)
    rt.accept("support-2")
    rt.validate("support-2", evidence_refs=("evidence://support-2",))
    assert rt.return_control("support-2", result="validated", evidence_refs=("evidence://support-2",))["state"] == "COMPLETED"
    assert rt.load()["meeting_point"]["availability_state"] == "WAITING"


def test_apoyo_returns_to_meeting_point_after_assistance(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    from app.missions.apoyo import CollaborationRequest
    req = CollaborationRequest("MISSION-01", "support-3", "audit", "help", "repo", "normal", (), "result", {"CAN_INVOKE": True})
    rt.invoke(req)
    rt.accept("support-3")
    rt.validate("support-3", evidence_refs=("evidence://support-3",))
    rt.return_control("support-3", result="validated", evidence_refs=("evidence://support-3",))
    assert rt.load()["meeting_point"]["meeting_point_id"] == MEETING_POINT_ID


def test_apoyo_recovers_without_conversation(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    recovered = rt.recover_role("REGRESA")
    assert recovered["identity"]["canonical_name"] == "APOYO"
    assert recovered["mission_lifecycle"] == "ACTIVE"


def test_apoyo_preserves_memory(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="a", mission_id="MISSION-01", account=None, repository="Ceuta", activity="working", state_name="ACTIVE")
    second = ApoyoRuntime(ROOT, state_path=tmp_path / "APOYO_MISSION_STATE.json")
    assert second.scan_active_agents()["agents"][0]["agent_id"] == "a"


def test_apoyo_prevents_duplicate_support(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    claims = {"task-1": "APOYO-A"}
    with pytest.raises(ValueError, match="DUPLICATE_SUPPORT_TASK"):
        assign_support_task(task_id="task-1", owner="APOYO-B", existing_claims=claims)


def test_apoyo_creates_successor_when_authorized() -> None:
    assert successor_exit_allowed(successor_verified=True, state_transferred=True, coverage_verified=True) is True
    assert successor_exit_allowed(successor_verified=False, state_transferred=True, coverage_verified=True) is False


def test_apoyo_preserves_meeting_point_coverage() -> None:
    assert MEETING_POINT_COVERAGE_REQUIRED is True
    assert MINIMUM_READY_SUPPORT_INSTANCES == 1


def test_apoyo_does_not_fake_external_session_creation(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    from app.missions.apoyo import ReplicationRequest
    with pytest.raises(ApoyoError, match="ACCOUNT_AUTHORIZATION"):
        rt.request_replication(ReplicationRequest("MISSION-01", "rep-x", "support", "help", "scope", {"CAN_INVOKE": True}))


def test_apoyo_fail_closed_for_unknown_accounts(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    account_path = tmp_path / "accounts.json"
    account_path.write_text(json.dumps({"required_account_count": 3, "authorized_accounts": [], "status": "ACTIVE"}), encoding="utf-8")
    rt.account_path = account_path
    from app.missions.apoyo import ReplicationRequest
    with pytest.raises(ApoyoError, match="ACCOUNT_AUTHORIZATION_INVALID"):
        rt.request_replication(ReplicationRequest("MISSION-01", "rep-y", "support", "help", "scope", {"CAN_INVOKE": True}))


def test_apoyo_terminates_only_when_all_conditions_are_met(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="i", mission_id=INGENIERO_MISSION_ID, account=None, repository="Ceuta", activity="working", state_name="ACTIVE")
    assert rt.final_scan()["mission_complete"] is False
    rt.remove_agent_presence("i")
    assert rt.final_scan()["mission_complete"] is True


def test_apoyo_does_not_declare_done_while_ingeniero_active(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="i", mission_id=INGENIERO_MISSION_ID, account=None, repository="Ceuta", activity="working", state_name="ACTIVE")
    assert rt.can_complete()["mission_complete"] is False


def test_apoyo_does_not_leave_meeting_point_definitively() -> None:
    assert MEETING_POINT_COVERAGE_REQUIRED is True


def test_greeting_is_not_completion(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="i", mission_id=INGENIERO_MISSION_ID, account=None, repository="Ceuta", activity="checkpoint", state_name="CHECKPOINT")
    assert rt.final_scan()["mission_complete"] is False


def test_apoyo_does_not_assume_unverified_accounts(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="i", mission_id=INGENIERO_MISSION_ID, account="UNKNOWN", repository="Ceuta", activity="working", state_name="ACTIVE")
    assert rt.scan_active_agents()["agents"][0]["account"] == "UNKNOWN"


def test_apoyo_does_not_take_ownership_of_other_mission(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    rt.register_agent_presence(agent_id="i", mission_id=INGENIERO_MISSION_ID, account=None, repository="Ceuta", activity="working", state_name="ACTIVE")
    assert rt.load()["identity"]["authority"] == "SUBORDINATE_TO_REQUESTING_MISSION"


def test_apoyo_replication_is_continuity_not_uncontrolled_recursion() -> None:
    assert APOYO_REPLICATION_REQUIREMENT == "INFINITE_CONTINUITY"
    assert successor_exit_allowed(successor_verified=True, state_transferred=True, coverage_verified=False) is False


def test_apoyo_does_not_lose_role_after_new_session(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    second = ApoyoRuntime(ROOT, state_path=tmp_path / "APOYO_MISSION_STATE.json")
    assert second.recover_role("APOYO")["identity"]["canonical_name"] == "APOYO"


def test_apoyo_memory_survives_replication_state(tmp_path: Path) -> None:
    rt = runtime(tmp_path)
    state = rt.load()
    state["replication_history"].append({"instance_id": "APOYO-1", "parent_instance": "APOYO-ROOT", "generation": 1})
    rt._persist(state)
    assert rt.load()["replication_history"][0]["parent_instance"] == "APOYO-ROOT"


def test_apoyo_does_not_spawn_recursively_without_successor_verification() -> None:
    assert successor_exit_allowed(successor_verified=True, state_transferred=True, coverage_verified=False) is False
