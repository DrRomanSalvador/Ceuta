import json
import shutil
from pathlib import Path

import pytest

from app.missions.evolution import MissionEvolutionEngine
from app.missions.evolution_runtime import EvolutionRuntimeError, MissionEvolutionRuntime

ROOT = Path(__file__).resolve().parents[1]


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_founder_zero_context_discovery_uses_canonical_registry_and_state():
    runtime = MissionEvolutionRuntime(ROOT)
    result = runtime.validate_zero_context("FOUNDER")
    assert result["passed"] is True
    assert result["mission_id"] == "FOUNDER"
    assert result["contract_exists"] is True
    assert result["state_exists"] is True
    assert result["next"] == "LOAD_CONTRACT → CHECK_AUTHORITY → CHECK_INPUTS → INVOKE"


def test_founder_admission_runtime_can_replay_transaction_without_mutating_real_registry(tmp_path):
    source_registry = ROOT / "docs/missions/MISSION_REGISTRY.json"
    registry = _load(source_registry)
    registry["missions"] = [m for m in registry["missions"] if m.get("mission_id") != "FOUNDER"]
    missions_root = tmp_path / "docs" / "missions"
    missions_root.mkdir(parents=True)
    (missions_root / "MISSION_REGISTRY.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    shutil.copytree(ROOT / "docs/missions/evolution", missions_root / "evolution")
    proposal_raw = _load(ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json")

    # Reconstruct the engine decision from persisted proposal data through the same public API.
    from tests.test_founder_evolution_admission import build_proposal, decide_founder
    proposal = build_proposal(proposal_raw)
    decision = decide_founder(proposal, registry["missions"])
    assert decision.decision == "ADMIT"

    runtime = MissionEvolutionRuntime(tmp_path)
    staged = runtime.stage_admission(decision, {"CAN_AUTHORIZE": True})
    assert staged.exists()
    committed = runtime.commit_staged(proposal.proposal_id, {"CAN_AUTHORIZE": True})
    assert committed["status"] == "COMMITTED"
    assert any(m.get("mission_id") == "FOUNDER" for m in _load(missions_root / "MISSION_REGISTRY.json")["missions"])
    assert (missions_root / "founder" / "INVOCATION_CONTRACT.json").exists()
    assert (missions_root / "founder" / "MISSION_STATE.json").exists()
    assert (missions_root / "founder" / "CANONICAL_MISSION_PROMPT.md").exists()


def test_founder_runtime_rejects_stale_registry_transaction(tmp_path):
    source_registry = _load(ROOT / "docs/missions/MISSION_REGISTRY.json")
    source_registry["missions"] = [m for m in source_registry["missions"] if m.get("mission_id") != "FOUNDER"]
    missions_root = tmp_path / "docs" / "missions"
    missions_root.mkdir(parents=True)
    registry_path = missions_root / "MISSION_REGISTRY.json"
    registry_path.write_text(json.dumps(source_registry, ensure_ascii=False), encoding="utf-8")
    (missions_root / "evolution" / "transactions").mkdir(parents=True)
    proposal_raw = _load(ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json")
    from tests.test_founder_evolution_admission import build_proposal, decide_founder
    proposal = build_proposal(proposal_raw)
    decision = decide_founder(proposal, source_registry["missions"])
    runtime = MissionEvolutionRuntime(tmp_path)
    runtime.stage_admission(decision, {"CAN_AUTHORIZE": True})
    mutated = _load(registry_path)
    mutated["status"] = "MUTATED_AFTER_STAGE"
    registry_path.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(EvolutionRuntimeError, match="STALE_REGISTRY_VERSION"):
        runtime.commit_staged(proposal.proposal_id, {"CAN_AUTHORIZE": True})
