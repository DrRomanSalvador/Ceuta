from __future__ import annotations


def optimize(values: tuple[float, ...], costs: tuple[float, ...], budget: float) -> tuple[int, ...]:
    if len(values) != len(costs) or budget < 0:
        raise ValueError("values/costs mismatch or invalid budget")
    chosen: list[int] = []
    remaining = budget
    for idx in sorted(range(len(values)), key=lambda i: values[i] / costs[i] if costs[i] > 0 else float("inf"), reverse=True):
        if costs[idx] <= remaining:
            chosen.append(idx)
            remaining -= costs[idx]
    return tuple(sorted(chosen))
