import multiprocessing
import tempfile
import unittest
from pathlib import Path

from .coordination import (
    Authority,
    CommandConflict,
    CommandState,
    CommandType,
    CoordinationStore,
    Coordinator,
    DeferredHypothesis,
    Mirror,
    MirrorAction,
    OwnershipConflict,
    StaleStateError,
)
from .event_log import load_jsonl, validate_chain


def _concurrent_claim(root: str, mirror_id: str, invocation_id: str, task_id: str, queue) -> None:
    store = CoordinationStore(Path(root) / "state.json", Path(root) / "events.jsonl")
    mirror = Mirror(instance_id=mirror_id, store=store)
    try:
        mirror.claim_subtask(invocation_id, task_id=task_id)
        queue.put((mirror_id, "CLAIMED"))
    except OwnershipConflict:
        queue.put((mirror_id, "CONFLICT"))


class CoordinationConstitutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = CoordinationStore(self.root / "state.json", self.root / "events.jsonl")
        self.coordinator = Coordinator(instance_id="COORD-A", store=self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def test_initial_state_is_zero_context_reconstructable(self):
        observed = self.coordinator.observe()
        self.assertEqual(observed["state_version"], 0)
        self.assertIn("agents", observed)
        self.assertIn("mirrors", observed)

    def test_agent_progressing_long_run_is_not_stall(self):
        self.coordinator.register_agent("ENGINEER-1", "MISSION-01", state="RUNNING", progress=True)
        self.assertEqual(self.coordinator.detect_execution("ENGINEER-1"), "LONG_RUNNING_PROGRESS_CONTINUE")

    def test_active_no_progress_is_distinguished(self):
        self.coordinator.register_agent("ENGINEER-1", "MISSION-01", state="ACTIVE", progress=False)
        self.assertEqual(self.coordinator.detect_execution("ENGINEER-1"), "ACTIVE_NO_PROGRESS_REVIEW")

    def test_valid_command_is_persisted_and_attributed(self):
        state = self.coordinator.issue(
            command_type=CommandType.CONTINUE, target="ENGINEER-1", mission="MISSION-01",
            reason="healthy progress", authority_basis=Authority.COORDINATOR.value,
            expected_effect="continue execution",
        )
        self.assertEqual(len(state["commands"]), 1)
        command = next(iter(state["commands"].values()))
        self.assertEqual(command["issuer"], "COORD-A")
        self.assertEqual(command["state"], CommandState.ISSUED.value)

    def test_invalid_authority_is_rejected(self):
        with self.assertRaises(CommandConflict):
            self.coordinator.issue(
                command_type=CommandType.PAUSE, target="ENGINEER-1", mission="MISSION-01",
                reason="x", authority_basis=Authority.AGENT.value, expected_effect="pause",
            )

    def test_redirect_requires_higher_authority(self):
        with self.assertRaises(CommandConflict):
            self.coordinator.issue(
                command_type=CommandType.REDIRECT, target="ENGINEER-1", mission="MISSION-01",
                reason="x", authority_basis=Authority.COORDINATOR.value, expected_effect="redirect",
            )

    def test_stale_coordinator_state_fails_closed(self):
        first = self.coordinator.observe()["state_version"]
        self.coordinator.register_agent("ENGINEER-1", "MISSION-01", expected_version=first)
        with self.assertRaises(StaleStateError):
            self.coordinator.issue(
                command_type=CommandType.CHECKPOINT, target="ENGINEER-1", mission="MISSION-01",
                reason="checkpoint", authority_basis=Authority.COORDINATOR.value,
                expected_effect="persist checkpoint", expected_version=first,
            )

    def test_pause_requires_checkpoint_first(self):
        self.coordinator.register_agent("ENGINEER-1", "MISSION-01")
        state = self.coordinator.checkpoint_then_pause(target="ENGINEER-1", mission="MISSION-01", checkpoint_id="CP-1")
        self.assertIn("CP-1", state["checkpoints"])
        self.assertEqual(next(reversed(state["commands"].values()))["command_type"], CommandType.PAUSE.value)

    def test_standby_requires_persisted_checkpoint(self):
        with self.assertRaises(Exception):
            self.coordinator.standby(target="ENGINEER-1", mission="MISSION-01", checkpoint_id="missing")
        self.coordinator.checkpoint_then_pause(target="ENGINEER-1", mission="MISSION-01", checkpoint_id="CP-1")
        state = self.coordinator.standby(target="ENGINEER-1", mission="MISSION-01", checkpoint_id="CP-1")
        self.assertTrue(state["commands"])

    def test_deferred_hypothesis_preserves_reasoning(self):
        hypothesis = DeferredHypothesis("H-1", "ENGINEER-1", "2026-09-16T12:00:00Z", "context", "reasoning", "ACTION-A", "valid coordinator order ACTION-B")
        state = self.coordinator.persist_deferred_hypothesis(hypothesis, mission_id="MISSION-01")
        self.assertEqual(state["deferred_hypotheses"]["H-1"]["reasoning"], "reasoning")

    def test_mirror_identity_and_ownership_are_separate(self):
        mirror = Mirror(instance_id="MIRROR-1", store=self.store)
        state = mirror.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="independent test", capability_required="tester", limits=["no ownership change"],
            priority="HIGH", authority=Authority.COORDINATOR.value, expected_result="validated test",
            action=MirrorAction.TEST, functional_role="tester", mission_owner="ENGINEER-1",
        )
        invocation = next(iter(state["mirrors"].values()))
        self.assertEqual(invocation["subtask_owner"], "MIRROR-1")
        self.assertEqual(invocation["mission_owner"], "ENGINEER-1")
        self.assertEqual(invocation["mirror_of"], "ENGINEER-1")

    def test_mirror_cannot_claim_foreign_invocation(self):
        mirror = Mirror(instance_id="MIRROR-1", store=self.store)
        state = mirror.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="review", capability_required="reviewer", limits=[], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="review", action=MirrorAction.REVIEW,
            functional_role="reviewer", mission_owner="ENGINEER-1",
        )
        mirror_id = next(iter(state["mirrors"]))
        foreign = Mirror(instance_id="MIRROR-2", store=self.store)
        with self.assertRaises(OwnershipConflict):
            foreign.claim_subtask(mirror_id, task_id="T-1")

    def test_two_mirrors_competing_for_same_task_have_single_owner(self):
        mirror_a = Mirror(instance_id="MIRROR-A", store=self.store)
        mirror_b = Mirror(instance_id="MIRROR-B", store=self.store)
        state_a = mirror_a.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="assist", capability_required="tester", limits=[], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="result", action=MirrorAction.TEST,
            functional_role="tester", mission_owner="ENGINEER-1",
        )
        state_b = mirror_b.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="duplicate", capability_required="tester", limits=[], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="result", action=MirrorAction.TEST,
            functional_role="tester", mission_owner="ENGINEER-1",
        )
        invocation_a = list(state_a["mirrors"])[-1]
        invocation_b = list(state_b["mirrors"])[-1]
        mirror_a.claim_subtask(invocation_a, task_id="T-1")
        with self.assertRaises(OwnershipConflict):
            mirror_b.claim_subtask(invocation_b, task_id="T-1")
        self.assertEqual(self.store.load()["tasks"]["T-1"]["subtask_owner"], "MIRROR-A")

    def test_integrated_engineer_coordinator_mirror_flow(self):
        self.coordinator.register_agent("ENGINEER-1", "MISSION-01", state="RUNNING", progress=True)
        self.assertEqual(self.coordinator.detect_execution("ENGINEER-1"), "LONG_RUNNING_PROGRESS_CONTINUE")
        command_state = self.coordinator.request_mirror(
            target_agent="ENGINEER-1", mission="MISSION-01", task="T-1", problem="independent validation",
            capability_required="tester", limits=["no ownership change"], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="validated result",
        )
        order_id = next(iter(command_state["commands"]))
        self.assertEqual(command_state["commands"][order_id]["command_type"], CommandType.REQUEST_MIRROR.value)
        mirror = Mirror(instance_id="MIRROR-1", store=self.store)
        invocation_state = mirror.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="independent validation", capability_required="tester", limits=["no ownership change"],
            priority="HIGH", authority=Authority.COORDINATOR.value, expected_result="validated result",
            action=MirrorAction.TEST, functional_role="tester", mission_owner="ENGINEER-1",
        )
        mirror_id = [k for k in invocation_state["mirrors"]][-1]
        mirror.claim_subtask(mirror_id, task_id="T-1")
        final_state = mirror.complete(mirror_id, result="validated", validated=True)
        handoff = final_state["handoffs"][-1]
        self.assertEqual(handoff["mission_owner"], "ENGINEER-1")
        self.assertEqual(handoff["subtask_owner"], "MIRROR-1")
        self.assertTrue(handoff["control_returned"])

    def test_two_processes_cannot_silently_overwrite_task_claim(self):
        root = self.root / "process"
        root.mkdir()
        seed = CoordinationStore(root / "state.json", root / "events.jsonl")
        mirror_a = Mirror(instance_id="MIRROR-A", store=seed)
        mirror_b = Mirror(instance_id="MIRROR-B", store=seed)
        state_a = mirror_a.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="concurrent claim", capability_required="tester", limits=[], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="one owner", action=MirrorAction.TEST,
            functional_role="tester", mission_owner="ENGINEER-1",
        )
        state_b = mirror_b.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="concurrent claim", capability_required="tester", limits=[], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="one owner", action=MirrorAction.TEST,
            functional_role="tester", mission_owner="ENGINEER-1",
        )
        invocation_a = list(state_a["mirrors"])[-1]
        invocation_b = list(state_b["mirrors"])[-1]
        q = multiprocessing.Queue()
        p1 = multiprocessing.Process(target=_concurrent_claim, args=(str(root), "MIRROR-A", invocation_a, "T-1", q))
        p2 = multiprocessing.Process(target=_concurrent_claim, args=(str(root), "MIRROR-B", invocation_b, "T-1", q))
        p1.start(); p2.start(); p1.join(); p2.join()
        outcomes = [q.get(), q.get()]
        self.assertEqual(sorted(result for _, result in outcomes), ["CLAIMED", "CONFLICT"])

    def test_event_lineage_is_hash_chained(self):
        self.coordinator.register_agent("ENGINEER-1", "MISSION-01")
        self.coordinator.issue(command_type=CommandType.CONTINUE, target="ENGINEER-1", mission="MISSION-01", reason="x", authority_basis=Authority.COORDINATOR.value, expected_effect="continue")
        events = load_jsonl(self.root / "events.jsonl")
        self.assertGreaterEqual(len(events), 2)
        validate_chain(events)

    def test_zero_context_recovers_mirror_result(self):
        mirror = Mirror(instance_id="MIRROR-1", store=self.store)
        state = mirror.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="recovery", capability_required="researcher", limits=[], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="recovered", action=MirrorAction.RESEARCH,
            functional_role="researcher", mission_owner="ENGINEER-1",
        )
        mirror_id = next(iter(state["mirrors"]))
        mirror.claim_subtask(mirror_id, task_id="T-1")
        mirror.complete(mirror_id, result="recovered", validated=True)
        new_instance = Mirror(instance_id="MIRROR-RECOVERED", store=self.store)
        recovered = new_instance.observe_recovery(mirror_id)
        self.assertEqual(recovered["result"], "recovered")
        self.assertEqual(recovered["mission_owner"], "ENGINEER-1")


if __name__ == "__main__":
    unittest.main()
