"""Runtime discovery and invocation contracts for the multi-mission control plane."""

from .registry import InvocationEnvelope, MissionRegistry, MissionRegistryError

__all__ = ["InvocationEnvelope", "MissionRegistry", "MissionRegistryError"]
