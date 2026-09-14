"""Linear-Gaussian state-space operations with explicit observation semantics.

This is an engineering substrate, not a universal territorial model. A model
must provide A, Q, H and R appropriate to the phenomenon before these
operations can be used. No causal interpretation is inferred from matrices.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True, slots=True)
class LinearStateSpace:
    transition: tuple[tuple[float, ...], ...]
    process_covariance: tuple[tuple[float, ...], ...]
    observation: tuple[tuple[float, ...], ...]
    observation_covariance: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        a = np.asarray(self.transition, dtype=float)
        q = np.asarray(self.process_covariance, dtype=float)
        h = np.asarray(self.observation, dtype=float)
        r = np.asarray(self.observation_covariance, dtype=float)
        if a.ndim != 2 or a.shape[0] != a.shape[1]:
            raise ValueError("transition matrix must be square")
        if q.shape != a.shape or h.ndim != 2 or h.shape[1] != a.shape[0] or r.shape != (h.shape[0], h.shape[0]):
            raise ValueError("state-space dimensions are inconsistent")
        for matrix in (a, q, h, r):
            if not np.all(np.isfinite(matrix)):
                raise ValueError("state-space matrices must be finite")
        if not np.allclose(q, q.T, atol=1e-10) or not np.allclose(r, r.T, atol=1e-10):
            raise ValueError("noise covariance matrices must be symmetric")
        if np.any(np.linalg.eigvalsh(q) < -1e-9) or np.any(np.linalg.eigvalsh(r) < -1e-9):
            raise ValueError("noise covariance matrices must be positive semidefinite")


@dataclass(frozen=True, slots=True)
class GaussianState:
    mean: tuple[float, ...]
    covariance: tuple[tuple[float, ...], ...]


class StateSpaceEngine:
    @staticmethod
    def predict(model: LinearStateSpace, state: GaussianState) -> GaussianState:
        a = np.asarray(model.transition, dtype=float)
        q = np.asarray(model.process_covariance, dtype=float)
        mean = np.asarray(state.mean, dtype=float)
        covariance = np.asarray(state.covariance, dtype=float)
        if mean.shape != (a.shape[0],) or covariance.shape != a.shape:
            raise ValueError("state dimensions do not match model")
        predicted_mean = a @ mean
        predicted_covariance = a @ covariance @ a.T + q
        predicted_covariance = (predicted_covariance + predicted_covariance.T) / 2
        return GaussianState(tuple(predicted_mean.tolist()), tuple(map(tuple, predicted_covariance.tolist())))

    @staticmethod
    def update(model: LinearStateSpace, state: GaussianState, observation: Sequence[float]) -> GaussianState:
        h = np.asarray(model.observation, dtype=float)
        r = np.asarray(model.observation_covariance, dtype=float)
        mean = np.asarray(state.mean, dtype=float)
        covariance = np.asarray(state.covariance, dtype=float)
        y = np.asarray(observation, dtype=float)
        if y.shape != (h.shape[0],):
            raise ValueError("observation dimension does not match model")
        innovation = y - h @ mean
        innovation_covariance = h @ covariance @ h.T + r
        try:
            gain = np.linalg.solve(innovation_covariance, h @ covariance).T
        except np.linalg.LinAlgError as exc:
            raise ValueError("observation covariance is singular") from exc
        updated_mean = mean + gain @ innovation
        identity = np.eye(len(mean))
        updated_covariance = (identity - gain @ h) @ covariance @ (identity - gain @ h).T + gain @ r @ gain.T
        updated_covariance = (updated_covariance + updated_covariance.T) / 2
        return GaussianState(tuple(updated_mean.tolist()), tuple(map(tuple, updated_covariance.tolist())))

    @staticmethod
    def innovation(model: LinearStateSpace, state: GaussianState, observation: Sequence[float]) -> tuple[float, ...]:
        h = np.asarray(model.observation, dtype=float)
        return tuple((np.asarray(observation, dtype=float) - h @ np.asarray(state.mean, dtype=float)).tolist())


__all__ = ["GaussianState", "LinearStateSpace", "StateSpaceEngine"]
