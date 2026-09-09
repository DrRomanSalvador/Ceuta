"""Tests for the non-operational system integrator skeleton."""

from __future__ import annotations

import math
import pytest

from app.core.system_integrator import (
    EpistemicStatus,
    build_system_view,
    compose_local_vulnerability,
    compose_cascade_potential,
    proxy_gate_tension_signal,
)


def test_local_vulnerability_high_when_load_near_capacity():
    v, status, _ = compose_local_vulnerability(capacity=100.0, load=95.0, sensitivity=0.8)
    assert status == EpistemicStatus.HYPOTHESIS_UNCALIBRATED
    assert 0.0 <= v <= 1.0
    v_low, _, _ = compose_local_vulnerability(capacity=100.0, load=10.0, sensitivity=0.1)
    assert v > v_low


def test_local_vulnerability_low_when_reserve_large():
    v, status, _ = compose_local_vulnerability(capacity=100.0, load=10.0, sensitivity=0.1)
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


"""Tests for the non-operational system integrator skeleton."""

from __future__ import annotations

import math
import pytest

from app.core.system_integrator import (
    EpistemicStatus,
    build_system_view,
    compose_local_vulnerability,
    compose_cascade_potential,
    proxy_gate_tension_signal,
)


def test_local_vulnerability_high_when_load_near_capacity():
    v, status, _ = compose_local_vulnerability(capacity=100.0, load=95.0, sensitivity=0.8)
    assert status == EpistemicStatus.HYPOTHESIS_UNCALIBRATED
    assert 0.0 <= v <= 1.0
    v_low, _, _ = compose_local_vulnerability(capacity=100.0, load=10.0, sensitivity=0.1)
    assert v > v_low


def test_local_vulnerability_low_when_reserve_large():
    v, status, _ = compose_local_vulnerability(capacity=100.0, load=10.0, sensitivity=0.1)
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
    
    