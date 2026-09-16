import unittest

from .control_plane import (
    ControlPlaneContract,
    HandoffState,
    MissionState,
    acquire_work_claim,
    can_modify_surface,
    reconcile,
    select_next_work,
    transition,
    validate_checkpoint,
    validate_completion_evidence,
    validate_dependency_graph,
    validate_handoff,
    validate_mission_contract,
    validate_no_self_authorization,
)


class ControlPlaneTests(unittest.TestCase):
    def test_illegal_unknown_to_complete_transition_is_rejected(self):
        with self.assertRaises(ValueError):
            transition(MissionState.UNKNOWN, MissionState.COMPLETE, authorized_actor="MISSION-01", evidence=["x"])

    def test_valid_transition_requires_evidence(self):
        record = transition(MissionState.READY, MissionState.ACTIVE, authorized_actor="MISSION-01", evidence=["commit"])
        self.assertEqual(record["to"], "ACTIVE")

    def test_control_plane_state_distinctions_exist(self):
        ControlPlaneContract().validate_distinctions()

    def test_work_claim_is_owner_bound(self):
        work = {"work_id": "W1", "mission_owner": "MISSION-01", "surface": "mission/a", "objective": "x", "status": "READY"}
        with self.assertRaises(PermissionError):
            acquire_work_claim(work, mission_id="MISSION-02", actor="agent-2", lease_id="L1")
        claim = acquire_work_claim(work, mission_id="MISSION-01", actor="agent-1", lease_id="L1")
        self.assertEqual(claim["status"], "ACTIVE")

    def test_surface_boundary_is_enforced(self):
        mission = {"mission_id": "MISSION-01", "allowed_write_surfaces": ["mission/control"], "forbidden_write_surfaces": ["security"]}
        self.assertTrue(can_modify_surface(mission_id="MISSION-01", surface="mission/control", mission=mission))
        self.assertFalse(can_modify_surface(mission_id="MISSION-01", surface="security", mission=mission))
        self.assertFalse(can_modify_surface(mission_id="MISSION-02", surface="mission/control", mission=mission))

    def test_dependency_graph_rejects_orphans_and_cycles(self):
        missions = [
            {"mission_id": "MISSION-01", "mission_name": "A", "mission_version": "1", "mission_class": "engineering", "mission_status": "ACTIVE", "mission_owner": "A", "authority_scope": "x", "repository_scope": "x", "allowed_write_surfaces": ["a"], "forbidden_write_surfaces": [], "inputs": [], "outputs": [], "dependencies": [], "dependents": [], "handoff_contract": "x", "validation_contract": "x", "state_source": "x", "current_objective": "x", "current_gap": "x", "next_authorized_action": "x", "completion_criteria": "x", "failure_policy": "x", "recovery_policy": "x"},
            {"mission_id": "MISSION-02", "mission_name": "B", "mission_version": "1", "mission_class": "science", "mission_status": "DEFINED", "mission_owner": "B", "authority_scope": "x", "repository_scope": "x", "allowed_write_surfaces": ["b"], "forbidden_write_surfaces": [], "inputs": [], "outputs": [], "dependencies": [], "dependents": [], "handoff_contract": "x", "validation_contract": "x", "state_source": "x", "current_objective": "x", "current_gap": "x", "next_authorized_action": "x", "completion_criteria": "x", "failure_policy": "x", "recovery_policy": "x"},
        ]
        with self.assertRaises(ValueError):
            validate_dependency_graph(missions, [{"source": "MISSION-01", "target": "MISSION-03"}])
        with self.assertRaises(ValueError):
            validate_dependency_graph(missions, [{"source": "MISSION-01", "target": "MISSION-02"}, {"source": "MISSION-02", "target": "MISSION-01"}])

    def test_handoff_cannot_be_integrated_without_integrated_at(self):
        handoff = {
            "handoff_id": "H1", "source_mission": "MISSION-02", "destination_mission": "MISSION-01",
            "timestamp": "2026-09-16T00:00:00Z", "source_commit": "abc", "finding": "f",
            "evidence": ["e"], "affected_surface": "s", "severity": "HIGH", "required_action": "a",
            "proposed_action": "p", "constraints": [], "dependencies": [], "validation_required": True,
            "acceptance_criteria": ["c"], "status": HandoffState.INTEGRATED.value,
        }
        with self.assertRaises(ValueError):
            validate_handoff(handoff)

    def test_waiting_work_requires_blocking_dependency(self):
        with self.assertRaises(ValueError):
            select_next_work([{ "work_id": "W", "status": "WAITING", "priority": "HIGH", "centrality": 1 }])

    def test_priority_selection_is_reproducible(self):
        items = [
            {"work_id": "B", "status": "READY", "priority": "HIGH", "centrality": 0.9, "blocking_dependencies": []},
            {"work_id": "A", "status": "READY", "priority": "CRITICAL", "centrality": 0.2, "blocking_dependencies": []},
        ]
        self.assertEqual(select_next_work(items)["work_id"], "A")

    def test_reconciliation_freezes_conflict(self):
        result = reconcile(documented="VERIFIED", actual="FAILED", evidence=["ci"])
        self.assertEqual(result["status"], "CONFLICTING")
        self.assertTrue(result["claim_frozen"])

    def test_checkpoint_contract(self):
        validate_checkpoint({
            "mission_id": "MISSION-01", "current_state": "ACTIVE", "current_objective": "x",
            "current_findings": [], "current_blockers": [], "current_handoffs": [], "completed_work": [],
            "uncompleted_work": [], "next_authorized_action": "x", "last_verified_commit": "abc", "validation_status": "NOT_ESTABLISHED",
        })

    def test_completion_requires_evidence_status(self):
        with self.assertRaises(ValueError):
            validate_completion_evidence({"work_id": "W", "artifact": "a", "verification_method": "t", "evidence_status": "DOCUMENTED"})

    def test_self_authorization_is_not_allowed(self):
        with self.assertRaises(PermissionError):
            validate_no_self_authorization("MISSION-01", "elevate-authority", human_authorization_required=True)


if __name__ == "__main__":
    unittest.main()
