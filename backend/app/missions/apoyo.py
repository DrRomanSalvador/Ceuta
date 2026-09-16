from __future__ import annotations

from typing import Any, Mapping

from .apoyo_core import ApoyoError, ApoyoRuntime as _ApoyoRuntime, CollaborationRequest, ReplicationRequest


class ApoyoRuntime(_ApoyoRuntime):
    """APOYO runtime with corrected live-slot, event, handoff and stale-writer invariants."""

    @staticmethod
    def _instance_is_live(state_or_instance: Mapping[str, Any], instance_id: str | None = None) -> bool:
        item = state_or_instance.get(instance_id) if instance_id is not None else state_or_instance
        return isinstance(item, Mapping) and item.get("state") not in {None, "WAITING", "RETIRED", "FINISHED"}

    def _event(self, state: dict[str, Any], event_type: str, **payload: Any) -> None:
        if "state" in payload:
            payload["agent_state"] = payload.pop("state")
        super()._event(state, event_type, **payload)

    def _persist(self, state: dict[str, Any]) -> None:
        with self._lock():
            current = self.load() if self.state_path.exists() else None
            if current is not None and state.get("state_version") != current.get("state_version"):
                raise ApoyoError("STALE_STATE_VERSION")
            state["state_version"] = self._version(state)
            state["meeting_point"]["last_checkpoint"] = state["state_version"]
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            import json
            import os
            import tempfile
            fd, tmp_name = tempfile.mkstemp(prefix=f".{self.state_path.name}.", dir=str(self.state_path.parent), text=True)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(state, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(tmp_name, self.state_path)
            finally:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)

    def return_control(self, request_id: str, *, result: str, evidence_refs: Any) -> dict[str, Any]:
        completed = super().return_control(request_id, result=result, evidence_refs=evidence_refs)
        state = self.load()
        instance_id = state["instance_id"]
        state["state"] = "WAITING_AT_MEETING_POINT"
        state["meeting_point"]["availability_state"] = "WAITING"
        state["meeting_point"]["current_instance"] = instance_id
        state["instances"][instance_id]["state"] = "WAITING_AT_MEETING_POINT"
        state["instances"][instance_id]["meeting_point_status"] = "OCCUPIED"
        self._event(state, "RETURNED_TO_MEETING_POINT", instance_id=instance_id, request_id=request_id)
        self._persist(state)
        return completed
