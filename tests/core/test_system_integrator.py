"""Tests for the CeutIA system-integration and spatial-proxy gates."""

from __future__ import annotations

import pytest

from app.core.system_integrator import (
    EpistemicStatus,
    build_system_view,
    compose_cascade_potential,
    compose_local_vulnerability,
    evaluate_spatial_proxy_gate,
    partial_correlation,
    proxy_gate_tension_signal,
)


def test_local_vulnerability_high_when_load_near_capacity():
    v, status, _ = compose_local_vulnerability(
        capacity=100.0, load=95.0, sensitivity=0.8
    )
    assert status == EpistemicStatus.HYPOTHESIS_UNCALIBRATED
    assert 0.0 <= v <= 1.0
    v_low, _, _ = compose_local_vulnerability(
        capacity=100.0, load=10.0, sensitivity=0.1
    )
    assert v > v_low


def test_local_vulnerability_low_when_load_is_small():
    v, status, _ = compose_local_vulnerability(
        capacity=100.0, load=10.0, sensitivity=0.1
    )
    assert status == EpistemicStatus.HYPOTHESIS_UNCALIBRATED
    assert v < 0.5


def test_cascade_potential_zero_when_coupling_zero():
    pot, status, _ = compose_cascade_potential(
        coupling=0.0, propagation=1.0, local_vulnerability=0.9
    )
    assert pot == pytest.approx(0.0)
    assert status == EpistemicStatus.HYPOTHESIS_UNCALIBRATED


def test_proxy_gate_blocks_when_data_insufficient():
    msg, status = proxy_gate_tension_signal(
        signal_predicts_composition_stronger_than_outcome=None,
        data_sufficient=False,
    )
    assert status == EpistemicStatus.BLOCKED
    assert "NO_VERIFICADO" in msg


def test_proxy_gate_proxy_risk():
    msg, status = proxy_gate_tension_signal(
        signal_predicts_composition_stronger_than_outcome=True,
        data_sufficient=True,
    )
    assert status == EpistemicStatus.PROXY_RISK
    assert "PROXY_RISK" in msg


def test_build_system_view_blocks_on_tension_without_data():
    view = build_system_view(
        capacity=50.0,
        load=40.0,
        tension_signal_present=True,
        tension_predicts_composition_stronger=None,
        composition_outcome_data_sufficient=False,
    )
    assert view.epistemic_status == EpistemicStatus.BLOCKED
    assert "NO_VERIFICADO" in view.proxy_gate_result


def test_partial_correlation_is_high_for_outcome_relationship_after_control():
    signal = tuple(float(i) for i in range(1, 21))
    control = tuple(float(i % 5) for i in range(1, 21))
    outcome = tuple(2.0 * s + 0.5 * c for s, c in zip(signal, control))

    value = partial_correlation(signal, outcome, control)
    assert value > 0.99


def test_spatial_proxy_gate_blocks_with_insufficient_sample():
    assessment = evaluate_spatial_proxy_gate(
        signal=[1.0, 2.0, 3.0],
        composition=[1.0, 2.0, 3.0],
        outcome=[1.0, 1.0, 2.0],
        minimum_sample_size=10,
    )
    assert assessment.status == EpistemicStatus.BLOCKED
    assert assessment.sample_size == 3
    assert assessment.signal_composition_association is None


def test_spatial_proxy_gate_flags_stronger_composition_association():
    composition = tuple(float(i) for i in range(1, 21))
    signal = composition
    outcome = tuple(float((i % 3) * 10) for i in range(1, 21))

    assessment = evaluate_spatial_proxy_gate(
        signal=signal,
        composition=composition,
        outcome=outcome,
        minimum_sample_size=10,
    )

    assert assessment.status == EpistemicStatus.PROXY_RISK
    assert assessment.signal_composition_association == pytest.approx(1.0)
    assert assessment.signal_outcome_association is not None
    assert assessment.signal_outcome_partial_association is not None


def test_spatial_proxy_gate_does_not_claim_safety_when_gate_passes():
    signal = tuple(float(i) for i in range(1, 21))
    composition = tuple(float(i % 5) for i in range(1, 21))
    outcome = signal

    assessment = evaluate_spatial_proxy_gate(
        signal=signal,
        composition=composition,
        outcome=outcome,
        minimum_sample_size=10,
    )

    assert assessment.status == EpistemicStatus.HYPOTHESIS_UNCALIBRATED
    assert "does not establish" in assessment.explanation
