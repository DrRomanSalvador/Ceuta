"""Mathematical representation of interactions in connected complex systems.

The purpose of this module is representational completeness, not the claim that
one universal equation describes every complex system. It provides a common
formal language for pairwise, higher-order, delayed, cross-scale, cross-layer,
feedback and constrained interactions.

For a state x(t), the generic continuous-time representation is

    dx/dt = F_ext(t,x) + F_int(t,x) + F_ctrl(t,x,u) + epsilon(t)

with

    F_int = sum_e K_e(t, tau_e) Phi_e(x(t-tau_e), z_e)

where e can be a pairwise edge or a higher-order hyperedge, K_e is a signed
coupling operator, tau_e is an optional delay, Phi_e is the interaction law,
and z_e carries scale/layer/context metadata. No causal interpretation is
implied by a mathematical edge alone.

For discrete systems the analogous transition is

    x_{k+1} = T_k(x_k, x_{k-d_1}, ..., u_k, w_k).

The algebra deliberately stores structure and assumptions separately from
numerical values so that observational, causal and model-generated relations
cannot be silently conflated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite
from typing import Mapping, Sequence


class RelationKind(StrEnum):
    ASSOCIATIONAL = "associational"
    CAUSAL = "causal"
    MECHANISTIC = "mechanistic"
    CONSTRAINT = "constraint"
    INFORMATIONAL = "informational"
    OBSERVATIONAL = "observational"
    UNKNOWN = "unknown"


class LayerKind(StrEnum):
    BIOLOGICAL = "biological"
    SOCIAL = "social"
    ECONOMIC = "economic"
    INSTITUTIONAL = "institutional"
    TECHNOLOGICAL = "technological"
    INFRASTRUCTURAL = "infrastructural"
    ENVIRONMENTAL = "environmental"
    POLITICAL = "political"
    INFORMATIONAL = "informational"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class SystemNode:
    node_id: str
    system_id: str
    layer: LayerKind
    scale: str
    variable: str

    def __post_init__(self) -> None:
        if not all((self.node_id, self.system_id, self.scale, self.variable)):
            raise ValueError("node identity, system, scale and variable are required")


@dataclass(frozen=True, slots=True)
class InteractionEdge:
    edge_id: str
    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]
    kind: RelationKind
    coupling: float
    delay: float = 0.0
    active_from: float | None = None
    active_until: float | None = None
    mechanism: str | None = None
    evidence_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.edge_id or not self.source_ids or not self.target_ids:
            raise ValueError("interaction requires source and target identities")
        if not isfinite(self.coupling):
            raise ValueError("coupling must be finite")
        if not isfinite(self.delay) or self.delay < 0:
            raise ValueError("delay must be finite and non-negative")
        if self.active_from is not None and not isfinite(self.active_from):
            raise ValueError("active_from must be finite")
        if self.active_until is not None and not isfinite(self.active_until):
            raise ValueError("active_until must be finite")
        if self.active_from is not None and self.active_until is not None and self.active_from >= self.active_until:
            raise ValueError("active interval must have positive duration")
        if self.kind in {RelationKind.CAUSAL, RelationKind.MECHANISTIC} and not self.mechanism:
            raise ValueError("causal/mechanistic relations require an explicit mechanism")

    @property
    def order(self) -> int:
        return len(self.source_ids)

    @property
    def is_higher_order(self) -> bool:
        return self.order > 2

    def active_at(self, time: float) -> bool:
        if not isfinite(time):
            raise ValueError("time must be finite")
        if self.active_from is not None and time < self.active_from:
            return False
        if self.active_until is not None and time >= self.active_until:
            return False
        return True


@dataclass(frozen=True, slots=True)
class ScaleCoupling:
    coupling_id: str
    source_scale: str
    target_scale: str
    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]
    weight: float
    aggregation: str
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.coupling_id or not self.source_scale or not self.target_scale:
            raise ValueError("scale coupling identity is incomplete")
        if not self.source_ids or not self.target_ids:
            raise ValueError("scale coupling requires source and target nodes")
        if not isfinite(self.weight):
            raise ValueError("scale coupling weight must be finite")
        if not self.aggregation:
            raise ValueError("aggregation rule is required")


@dataclass(frozen=True, slots=True)
class FeedbackLoop:
    loop_id: str
    edge_ids: tuple[str, ...]
    sign: int
    gain: float
    delay: float = 0.0

    def __post_init__(self) -> None:
        if not self.loop_id or len(self.edge_ids) < 2:
            raise ValueError("feedback loop requires at least two edges")
        if self.sign not in (-1, 1):
            raise ValueError("feedback sign must be -1 or +1")
        if not isfinite(self.gain) or self.gain < 0:
            raise ValueError("feedback gain must be finite and non-negative")
        if not isfinite(self.delay) or self.delay < 0:
            raise ValueError("feedback delay must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class Constraint:
    constraint_id: str
    expression: str
    kind: str
    tolerance: float = 0.0
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.constraint_id or not self.expression or not self.kind:
            raise ValueError("constraint requires identity, expression and kind")
        if not isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("constraint tolerance must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class InteractionNetwork:
    nodes: tuple[SystemNode, ...]
    edges: tuple[InteractionEdge, ...]
    scale_couplings: tuple[ScaleCoupling, ...] = ()
    feedback_loops: tuple[FeedbackLoop, ...] = ()
    constraints: tuple[Constraint, ...] = ()
    time_semantics: str = "continuous"

    def __post_init__(self) -> None:
        node_ids = {node.node_id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("node IDs must be unique")
        edge_ids = {edge.edge_id for edge in self.edges}
        if len(edge_ids) != len(self.edges):
            raise ValueError("edge IDs must be unique")
        for edge in self.edges:
            if not set(edge.source_ids) <= node_ids or not set(edge.target_ids) <= node_ids:
                raise ValueError(f"edge {edge.edge_id} references unknown node")
        for coupling in self.scale_couplings:
            if not set(coupling.source_ids) <= node_ids or not set(coupling.target_ids) <= node_ids:
                raise ValueError(f"scale coupling {coupling.coupling_id} references unknown node")
        if self.time_semantics not in {"continuous", "discrete"}:
            raise ValueError("time_semantics must be continuous or discrete")

    def adjacency(self, *, time: float | None = None) -> dict[tuple[str, str], float]:
        """Return the pairwise projection of active edges.

        Higher-order edges are intentionally excluded from this projection;
        collapsing a hyperedge into pairwise edges loses interaction order.
        """
        result: dict[tuple[str, str], float] = {}
        for edge in self.edges:
            if edge.order != 1 and edge.order != 2:
                continue
            if time is not None and not edge.active_at(time):
                continue
            for source in edge.source_ids:
                for target in edge.target_ids:
                    result[(source, target)] = result.get((source, target), 0.0) + edge.coupling
        return result

    def interaction_order_distribution(self) -> dict[int, int]:
        distribution: dict[int, int] = {}
        for edge in self.edges:
            distribution[edge.order] = distribution.get(edge.order, 0) + 1
        return distribution

    def dependency_closure(self, node_id: str) -> frozenset[str]:
        """Compute directed structural reachability without asserting causality."""
        node_ids = {node.node_id for node in self.nodes}
        if node_id not in node_ids:
            raise ValueError("unknown node")
        reached = {node_id}
        changed = True
        while changed:
            changed = False
            for edge in self.edges:
                if set(edge.source_ids) & reached:
                    before = len(reached)
                    reached.update(edge.target_ids)
                    changed |= len(reached) != before
        return frozenset(reached)

    def feedback_gain_bound(self) -> float:
        """Return the maximum declared loop gain; this is not a stability proof."""
        return max((loop.gain for loop in self.feedback_loops), default=0.0)


@dataclass(frozen=True, slots=True)
class InteractionEquation:
    """A fully specified symbolic dynamic equation for one target variable."""

    target_id: str
    intrinsic_term: str
    interaction_terms: tuple[str, ...]
    control_term: str | None
    disturbance_term: str | None
    delay_arguments: tuple[str, ...]
    assumptions: tuple[str, ...] = ()

    def render(self) -> str:
        rhs = [self.intrinsic_term, *self.interaction_terms]
        if self.control_term:
            rhs.append(self.control_term)
        if self.disturbance_term:
            rhs.append(self.disturbance_term)
        return f"d({self.target_id})/dt = " + " + ".join(rhs)


class InteractionAlgebra:
    """Builds equations while preserving interaction order and semantics."""

    @staticmethod
    def equation_for(network: InteractionNetwork, target_id: str) -> InteractionEquation:
        if target_id not in {node.node_id for node in network.nodes}:
            raise ValueError("unknown target")
        terms: list[str] = []
        delays: list[str] = []
        for edge in network.edges:
            if target_id not in edge.target_ids:
                continue
            arguments = ", ".join(f"x[{source}]" for source in edge.source_ids)
            if edge.delay:
                arguments = ", ".join(f"x[{source}](t-{edge.delay:g})" for source in edge.source_ids)
                delays.append(edge.edge_id)
            relation = f"K[{edge.edge_id}]·Phi[{edge.edge_id}]({arguments})"
            terms.append(relation)
        return InteractionEquation(
            target_id=target_id,
            intrinsic_term=f"F[{target_id}](x,t)",
            interaction_terms=tuple(terms),
            control_term="U(t,x,u)" if any(edge.kind == RelationKind.MECHANISTIC for edge in network.edges if target_id in edge.target_ids) else None,
            disturbance_term="epsilon(t)" if any(edge.kind == RelationKind.OBSERVATIONAL for edge in network.edges if target_id in edge.target_ids) else None,
            delay_arguments=tuple(delays),
            assumptions=(
                "interaction edges are not causal unless explicitly classified and mechanistically supported",
                "higher-order interactions are not reduced to pairwise projections",
                "time-varying activation and delays remain explicit",
            ),
        )
