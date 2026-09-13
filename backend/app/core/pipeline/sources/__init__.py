"""Source adapters for the CeutIA event pipeline."""

from .adapter import ProvenanceRegistry, SourceAdapter, SourceEnvelope
from .deduplication import DeduplicationDecision, EvidenceCluster, EvidenceDeduplicator
from .real_base import RealSourceAdapter, RealSourceEnvelope, SourceObservation, canonicalize_uri
from .synthetic import SyntheticSource

__all__ = [
    "ProvenanceRegistry",
    "SourceAdapter",
    "SourceEnvelope",
    "RealSourceAdapter",
    "RealSourceEnvelope",
    "SourceObservation",
    "EvidenceDeduplicator",
    "EvidenceCluster",
    "DeduplicationDecision",
    "canonicalize_uri",
    "SyntheticSource",
]
