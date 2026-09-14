"""Strict temporal fold construction for longitudinal validation.

Training observations are strictly earlier than the test interval. A purge gap
can additionally remove observations immediately before the test interval.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .longitudinal_validation import LongitudinalRecord


@dataclass(frozen=True, slots=True)
class TemporalDesignFold:
    fold: int
    train_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    train_start: float
    train_end_exclusive: float
    purge_start: float
    test_start: float
    test_end_exclusive: float


def strict_rolling_origin(
    records: Sequence[LongitudinalRecord],
    *,
    initial_train_duration: float,
    test_duration: float,
    step: float,
    purge_gap: float = 0.0,
    expanding: bool = True,
) -> tuple[TemporalDesignFold, ...]:
    """Construct folds with strict train-time < test-time separation."""
    if initial_train_duration <= 0 or test_duration <= 0 or step <= 0 or purge_gap < 0:
        raise ValueError("durations and step must be positive; purge_gap cannot be negative")
    if not records:
        raise ValueError("records must be non-empty")
    minimum = min(r.time for r in records)
    maximum = max(r.time for r in records)
    origin = minimum + initial_train_duration
    folds: list[TemporalDesignFold] = []
    fold_number = 0
    while origin + purge_gap + test_duration <= maximum:
        test_start = origin + purge_gap
        test_end = test_start + test_duration
        train_start = minimum if expanding else origin - initial_train_duration
        train = tuple(
            i for i, r in enumerate(records)
            if train_start <= r.time < origin
        )
        test = tuple(
            i for i, r in enumerate(records)
            if test_start <= r.time < test_end
        )
        if train and test:
            if max(records[i].time for i in train) >= min(records[i].time for i in test):
                raise RuntimeError("temporal leakage detected")
            folds.append(
                TemporalDesignFold(
                    fold_number,
                    train,
                    test,
                    train_start,
                    origin,
                    origin,
                    test_start,
                    test_end,
                )
            )
            fold_number += 1
        origin += step
    if not folds:
        raise ValueError("temporal design produced no valid folds")
    return tuple(folds)
