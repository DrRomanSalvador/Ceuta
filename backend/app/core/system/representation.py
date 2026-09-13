"""Exhaustive domain-neutral representation primitives for complex systems."""
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from ..errors import ContractViolation, TemporalViolation

@dataclass(frozen=True, slots=True)
class SystemEntity:
    entity_id: str
    parent_id: str | None = None
    scale: str = "system"
    domain: str = "generic"
    attributes: Mapping[str, object] = None
    def __post_init__(self):
        if not self.entity_id: raise ContractViolation("entity_id required")
        if not self.scale or not self.domain: raise ContractViolation("scale and domain required")

@dataclass(frozen=True, slots=True)
class SystemVariable:
    variable_id: str
    entity_id: str
    unit: str | None = None
    latent: bool = False
    observable: bool = True
    spatial_scale: str = "system"
    temporal_scale: str = "event"
    def __post_init__(self):
        if not self.variable_id or not self.entity_id: raise ContractViolation("variable and entity required")
        if self.latent and self.observable: raise ContractViolation("latent variable cannot be directly observable")

@dataclass(frozen=True, slots=True)
class SystemBoundary:
    system_id: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    constraints: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class SystemRepresentation:
    system_id: str
    as_of: datetime
    entities: tuple[SystemEntity, ...]
    variables: tuple[SystemVariable, ...]
    boundary: SystemBoundary
    scales: tuple[str, ...]
    def __post_init__(self):
        if not self.system_id: raise ContractViolation("system_id required")
        if self.as_of.tzinfo is None: raise TemporalViolation("as_of must be timezone-aware")
        if not self.entities or not self.variables: raise ContractViolation("representation requires entities and variables")
        if len({x.entity_id for x in self.entities}) != len(self.entities): raise ContractViolation("duplicate entities")
        if len({x.variable_id for x in self.variables}) != len(self.variables): raise ContractViolation("duplicate variables")
