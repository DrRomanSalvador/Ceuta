from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "backend/app/core/ingestion/orchestrator.py",
    "backend/app/core/ingestion/event_resolution.py",
    "backend/app/core/ingestion/source_health.py",
    "backend/app/core/ingestion/schema_drift.py",
    "backend/app/core/ingestion/replay.py",
    "backend/app/core/serpiente/source_dependency_graph.py",
    "backend/app/core/serpiente/entity_resolution.py",
    "backend/app/core/serpiente/dynamic_graph.py",
    "backend/app/core/serpiente/weak_signals.py",
    "backend/app/core/serpiente/regime_detection.py",
    "backend/app/core/serpiente/cascading_risk.py",
    "backend/app/core/serpiente/hypothesis_engine.py",
    "backend/app/core/serpiente/scenario_engine.py",
    "backend/app/core/serpiente/multimodel_forecaster.py",
    "backend/app/core/serpiente/calibration_engine.py",
    "backend/app/core/forecasting/forecast_distribution.py",
    "backend/app/core/calibration/drift.py",
    "backend/app/core/calibration/model_governance.py",
    "backend/app/core/learning/prospective_loop.py",
    "backend/app/core/decision/decision_engine.py",
    "backend/app/core/decision/tradeoff_engine.py",
    "backend/app/core/decision/counterfactual_engine.py",
    "backend/app/core/spatial/spatial_engine.py",
    "backend/app/core/spatial/flow_model.py",
    "backend/app/core/simulation/digital_twin_core.py",
    "backend/app/core/simulation/agent_stress.py",
    "backend/app/core/governance/llm_guard.py",
    "backend/app/core/governance/traceability.py",
    "backend/app/core/governance/humility_engine.py",
    "backend/app/core/governance/adversarial.py",
    "backend/app/core/governance/information_operations.py",
    "backend/app/core/governance/red_team.py",
    "backend/app/core/governance/validation.py",
    "backend/app/core/governance/incident_ledger.py",
    "backend/app/core/governance/information_firewall.py",
    "backend/app/core/governance/evidence_layer.py",
    "backend/app/core/privacy/aggregation_layer.py",
    "backend/app/core/resilience/checkpointing.py",
    "backend/app/core/resilience/emergency_degradation.py",
    "backend/app/core/resilience/failover.py",
    "tests/test_complex_systems_completion.py",
)

for relative in REQUIRED:
    if not (ROOT / relative).is_file():
        raise SystemExit(f"MISSING: {relative}")

print(f"PASS: phases 4-8 implementation inventory complete ({len(REQUIRED)} required files)")
print("CI execution intentionally deferred to the final validation step.")
