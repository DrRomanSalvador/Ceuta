"""Fetch external source data through the canonical CeutIA evidence contract.

This module deliberately does not create a parallel ``VerifiedData`` model.
Fetched content remains an observation with explicit uncertainty and epistemic
status until the canonical epistemology pipeline evaluates it.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any

import requests

from backend.app.core.p0_contracts import (
    EpistemicStatus,
    EvidenceContract,
    ProvenanceLink,
    SourceRelation,
    Uncertainty,
)

from .config import DataSource, SystemConfig

logger = logging.getLogger(__name__)


class DataFetcher:
    """Obtain source payloads without assigning them truth or verification status."""

    def __init__(self, config: SystemConfig | None = None):
        self.config = config or SystemConfig()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "CeutIA/1.0 (Auditable Observation Fetcher)",
                "Accept": "application/json",
            }
        )

    def fetch_from_source(self, source: DataSource) -> EvidenceContract | None:
        """Fetch a source and admit the result only as canonical evidence."""
        try:
            data = self._fetch_api(source) if source.api_endpoint else self._fetch_web(source)
            if data is None:
                logger.warning("No se pudieron obtener datos de %s", source.name)
                return None

            observed_at = datetime.now(UTC)
            payload = json.dumps(data, sort_keys=True, default=str)
            evidence_id = "EVD-" + hashlib.sha256(
                f"{source.name}|{source.url}|{payload}|{observed_at.isoformat()}".encode()
            ).hexdigest()[:24]
            source_version = source.last_verified or "UNKNOWN"

            return EvidenceContract(
                evidence_id=evidence_id,
                claim=payload,
                source_id=source.name,
                publication_time=None,
                event_time=None,
                observed_at=observed_at,
                ingestion_time=observed_at,
                revision_time=None,
                uncertainty=Uncertainty(
                    kind="unknown",
                    confidence=None,
                    description="Fetched payload has not yet undergone epistemic validation.",
                ),
                epistemic_status=EpistemicStatus.UNKNOWN,
                source_relation=SourceRelation.UNKNOWN,
                provenance=(
                    ProvenanceLink(
                        source_id=source.name,
                        source_version=source_version,
                        relation=SourceRelation.UNKNOWN,
                        transformation="external-source-fetch-to-canonical-evidence",
                    ),
                ),
                limitations=(
                    "Retrieval does not establish truth, corroboration, causality, "
                    "source independence, or publication-time availability."
                ,),
            )
        except (ValueError, requests.RequestException, TypeError, json.JSONDecodeError) as exc:
            logger.error("Error obteniendo datos de %s: %s", source.name, exc)
            return None

    def _fetch_api(self, source: DataSource) -> Any | None:
        """Obtain a payload through the configured API endpoint."""
        try:
            response = self.session.get(source.api_endpoint, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.warning("API falló para %s: %s", source.name, exc)
            return None

    def _fetch_web(self, source: DataSource) -> Any | None:
        """Fetch a web source placeholder without claiming verification."""
        logger.info("Web scraping de %s (simulado)", source.url)
        return {"status": "fetched", "url": source.url}

    def fetch_all_sources(self) -> list[EvidenceContract]:
        """Fetch all configured sources as canonical, unverified evidence."""
        evidence: list[EvidenceContract] = []
        for source in self.config.OFFICIAL_SOURCES:
            logger.info("Obteniendo datos de %s...", source.name)
            item = self.fetch_from_source(source)
            if item is not None:
                evidence.append(item)
        logger.info(
            "Datos obtenidos de %d/%d fuentes",
            len(evidence),
            len(self.config.OFFICIAL_SOURCES),
        )
        return evidence

    def get_latest_data(self, source_name: str) -> EvidenceContract | None:
        """Fetch the configured source as canonical evidence."""
        sources = [s for s in self.config.OFFICIAL_SOURCES if s.name == source_name]
        return self.fetch_from_source(sources[0]) if sources else None
