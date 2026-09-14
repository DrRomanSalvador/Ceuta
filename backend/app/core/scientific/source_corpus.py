"""Persistent scientific corpus and cross-architectural impact map.

The corpus is infrastructure, not documentation. Sources are immutable records
with explicit epistemic classification, provenance and versioning. Impact records
make the path from evidence to mechanism, architecture, validation and mission
machine-readable without upgrading hypotheses into facts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
import sqlite3


class CorpusSourceType(StrEnum):
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CONTROLLED_EVIDENCE = "randomized_controlled_evidence"
    OBSERVATIONAL = "observational_evidence"
    LONGITUDINAL = "longitudinal_cohort"
    METHODOLOGICAL = "methodological_statistical"
    CAUSAL_INFERENCE = "causal_inference"
    FORECASTING = "forecasting"
    DECISION_THEORY = "decision_theory"
    MECHANISM_DESIGN = "mechanism_design"
    COMPLEX_SYSTEMS = "complex_systems"
    NETWORK_SCIENCE = "network_science"
    EARLY_WARNING = "early_warning"
    GUIDELINE = "guideline_consensus"
    GOVERNMENTAL = "governmental"
    INTERNATIONAL = "european_international_institution"
    STANDARD = "technical_standard"
    INSTITUTIONAL_REPORT = "institutional_report"
    OTHER = "other"


class CorpusEvidenceLevel(StrEnum):
    META_ANALYTIC = "meta_analytic"
    SYSTEMATIC_REVIEW = "systematic_review"
    CONTROLLED = "controlled"
    LONGITUDINAL = "longitudinal"
    OBSERVATIONAL = "observational"
    METHODOLOGICAL = "methodological"
    CONSENSUS = "consensus"
    OFFICIAL = "official"
    CONTEXTUAL = "contextual"


class ImpactRelation(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    MODIFIES = "modifies"
    COMPLEMENTS = "complements"
    DUPLICATES = "duplicates"
    TRANSLATES = "translates"
    DEPENDS_ON = "depends_on"


class ValidationStatus(StrEnum):
    IMPLEMENTED = "implemented_pending_validation"
    INTERNALLY_VALIDATED = "internally_validated"
    PROSPECTIVE_REQUIRED = "prospective_validation_required"
    EXTERNAL_REQUIRED = "external_validation_required"
    BLOCKED = "blocked_by_missing_observation"


@dataclass(frozen=True, slots=True)
class RetrievalMetadata:
    retrieved_at: str
    retrieval_method: str
    retriever: str
    content_fingerprint: str
    canonical_url: str = ""

    def __post_init__(self) -> None:
        if not self.retrieved_at:
            raise ValueError("retrieved_at is required")
        if len(self.content_fingerprint) != 64:
            raise ValueError("content_fingerprint must be SHA-256")


@dataclass(frozen=True, slots=True)
class ScientificSourceRecord:
    source_id: str
    title: str
    authors: tuple[str, ...]
    year: int
    identifier: str
    official_url: str
    source_type: CorpusSourceType
    evidence_level: CorpusEvidenceLevel
    methodology: str
    population_context: str
    domain: str
    phenomenon: tuple[str, ...]
    findings: tuple[str, ...]
    limitations: tuple[str, ...]
    applicability: tuple[str, ...]
    relevant_mechanism: tuple[str, ...]
    ceutia_components: tuple[str, ...]
    implementation_implications: tuple[str, ...]
    validation_requirements: tuple[str, ...]
    provenance: str
    client_contexts: tuple[str, ...] = ()
    question_types: tuple[str, ...] = ()
    risk_levels: tuple[str, ...] = ()
    response_types: tuple[str, ...] = ()
    contexts: tuple[str, ...] = ()
    version: int = 1
    retrieval: RetrievalMetadata | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.title or not self.identifier:
            raise ValueError("source_id, title and identifier are required")
        if not 1000 <= self.year <= 3000:
            raise ValueError("year must be plausible")
        if self.version < 1:
            raise ValueError("version must be >= 1")

    @property
    def record_hash(self) -> str:
        return _digest(self)


@dataclass(frozen=True, slots=True)
class ScientificImpactMap:
    impact_id: str
    source_ids: tuple[str, ...]
    phenomenon: str
    supported_claim: str
    evidence_level: str
    valid_context: str
    limitations: tuple[str, ...]
    mechanism: tuple[str, ...]
    existing_components: tuple[str, ...]
    contradictions_or_modifications: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    implementation_now: tuple[str, ...]
    integration_requirements: tuple[str, ...]
    tests_required: tuple[str, ...]
    internal_validation: tuple[str, ...]
    external_validation: tuple[str, ...]
    dependencies: tuple[str, ...]
    mission_queue: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    identifiability: str = ""
    applicability_boundary: str = ""
    validation_status: ValidationStatus = ValidationStatus.IMPLEMENTED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.impact_id or not self.source_ids or not self.phenomenon:
            raise ValueError("impact_id, source_ids and phenomenon are required")

    @property
    def impact_hash(self) -> str:
        return _digest(self)


@dataclass(frozen=True, slots=True)
class ScientificRelation:
    source_id: str
    related_source_id: str
    relation: ImpactRelation
    rationale: str
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.source_id == self.related_source_id:
            raise ValueError("self relation is invalid")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be in [0,1]")


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in sorted(value.items(), key=lambda x: str(x[0]))}
    return value


def _canonical(value: object) -> str:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


class ScientificSourceCorpus:
    """Append-only SQLite corpus for sources, relations, impacts and missions."""

    _LEVEL_RANK = {
        CorpusEvidenceLevel.META_ANALYTIC: 9,
        CorpusEvidenceLevel.SYSTEMATIC_REVIEW: 8,
        CorpusEvidenceLevel.CONTROLLED: 7,
        CorpusEvidenceLevel.LONGITUDINAL: 6,
        CorpusEvidenceLevel.OBSERVATIONAL: 5,
        CorpusEvidenceLevel.METHODOLOGICAL: 4,
        CorpusEvidenceLevel.CONSENSUS: 4,
        CorpusEvidenceLevel.OFFICIAL: 4,
        CorpusEvidenceLevel.CONTEXTUAL: 2,
    }

    def __init__(self, storage_path: str) -> None:
        if not storage_path:
            raise ValueError("storage_path is required")
        self.storage_path = storage_path
        self._init_db()

    def _db(self) -> sqlite3.Connection:
        return sqlite3.connect(self.storage_path)

    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_sources (
                source_id TEXT NOT NULL, version INTEGER NOT NULL, payload TEXT NOT NULL,
                record_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                PRIMARY KEY(source_id, version)
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_relations (
                source_id TEXT NOT NULL, related_source_id TEXT NOT NULL,
                relation TEXT NOT NULL, rationale TEXT NOT NULL, confidence REAL NOT NULL,
                PRIMARY KEY(source_id, related_source_id, relation)
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_impacts (
                impact_id TEXT PRIMARY KEY, source_ids TEXT NOT NULL, payload TEXT NOT NULL,
                impact_hash TEXT NOT NULL, created_at TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_missions (
                mission_id TEXT PRIMARY KEY, impact_id TEXT NOT NULL, mission TEXT NOT NULL,
                status TEXT NOT NULL, created_at TEXT NOT NULL
            )""")

    def register(self, source: ScientificSourceRecord) -> None:
        payload = _canonical(source)
        with self._db() as db:
            if db.execute("SELECT 1 FROM scientific_sources WHERE source_id=? AND version=?", (source.source_id, source.version)).fetchone():
                raise ValueError(f"source version already exists: {source.source_id}@{source.version}")
            db.execute("INSERT INTO scientific_sources VALUES(?,?,?,?,?)", (source.source_id, source.version, payload, source.record_hash, datetime.now(timezone.utc).isoformat()))

    def get(self, source_id: str, version: int | None = None) -> ScientificSourceRecord:
        with self._db() as db:
            row = db.execute(
                "SELECT payload FROM scientific_sources WHERE source_id=? AND (? IS NULL OR version=?) ORDER BY version DESC LIMIT 1",
                (source_id, version, version),
            ).fetchone()
        if not row:
            raise KeyError(source_id)
        return _decode_source(json.loads(row[0]))

    def all_latest(self) -> tuple[ScientificSourceRecord, ...]:
        with self._db() as db:
            rows = db.execute("""SELECT s.payload FROM scientific_sources s JOIN (
                SELECT source_id, MAX(version) version FROM scientific_sources GROUP BY source_id
            ) latest ON latest.source_id=s.source_id AND latest.version=s.version ORDER BY s.source_id""").fetchall()
        return tuple(_decode_source(json.loads(row[0])) for row in rows)

    def select(
        self,
        *,
        client: str = "",
        question_type: str = "",
        domain: str = "",
        risk_level: str = "",
        response_type: str = "",
        context: str = "",
        minimum_evidence_level: CorpusEvidenceLevel = CorpusEvidenceLevel.CONTEXTUAL,
    ) -> tuple[ScientificSourceRecord, ...]:
        minimum = self._LEVEL_RANK[minimum_evidence_level]
        candidates = [
            source for source in self.all_latest()
            if self._LEVEL_RANK[source.evidence_level] >= minimum
            and (not client or not source.client_contexts or client in source.client_contexts)
            and (not question_type or not source.question_types or question_type in source.question_types)
            and (not domain or source.domain == domain)
            and (not risk_level or not source.risk_levels or risk_level in source.risk_levels)
            and (not response_type or not source.response_types or response_type in source.response_types)
            and (not context or not source.contexts or context in source.contexts)
        ]
        candidates.sort(key=lambda source: (
            domain == source.domain if domain else False,
            risk_level in source.risk_levels if risk_level and source.risk_levels else False,
            question_type in source.question_types if question_type and source.question_types else False,
            _score(source.evidence_level),
            source.year,
            source.source_id,
        ), reverse=True)
        return tuple(candidates)

    def add_relation(self, relation: ScientificRelation) -> None:
        with self._db() as db:
            if not db.execute("SELECT 1 FROM scientific_sources WHERE source_id=?", (relation.source_id,)).fetchone():
                raise KeyError(relation.source_id)
            if not db.execute("SELECT 1 FROM scientific_sources WHERE source_id=?", (relation.related_source_id,)).fetchone():
                raise KeyError(relation.related_source_id)
            db.execute("INSERT OR IGNORE INTO scientific_relations VALUES(?,?,?,?,?)", (relation.source_id, relation.related_source_id, relation.relation.value, relation.rationale, relation.confidence))

    def add_impact(self, impact: ScientificImpactMap) -> None:
        with self._db() as db:
            for source_id in impact.source_ids:
                if not db.execute("SELECT 1 FROM scientific_sources WHERE source_id=?", (source_id,)).fetchone():
                    raise KeyError(source_id)
            payload = _canonical(impact)
            db.execute("INSERT INTO scientific_impacts VALUES(?,?,?,?,?)", (impact.impact_id, _canonical(impact.source_ids), payload, impact.impact_hash, impact.created_at))
            for mission in impact.mission_queue:
                mission_id = _digest((impact.impact_id, mission))
                db.execute("INSERT OR IGNORE INTO scientific_missions VALUES(?,?,?,?,?)", (mission_id, impact.impact_id, mission, "open", impact.created_at))

    def relations(self, source_id: str) -> tuple[ScientificRelation, ...]:
        with self._db() as db:
            rows = db.execute("SELECT source_id,related_source_id,relation,rationale,confidence FROM scientific_relations WHERE source_id=? ORDER BY related_source_id", (source_id,)).fetchall()
        return tuple(ScientificRelation(a, b, ImpactRelation(c), d, e) for a, b, c, d, e in rows)

    def impacts(self) -> tuple[ScientificImpactMap, ...]:
        with self._db() as db:
            rows = db.execute("SELECT payload FROM scientific_impacts ORDER BY created_at, impact_id").fetchall()
        return tuple(_decode_impact(json.loads(row[0])) for row in rows)

    def missions(self, status: str | None = None) -> tuple[tuple[str, str, str], ...]:
        with self._db() as db:
            if status is None:
                rows = db.execute("SELECT mission_id,mission,status FROM scientific_missions ORDER BY created_at,mission_id").fetchall()
            else:
                rows = db.execute("SELECT mission_id,mission,status FROM scientific_missions WHERE status=? ORDER BY created_at,mission_id", (status,)).fetchall()
        return tuple(rows)

    def verify_integrity(self) -> bool:
        with self._db() as db:
            rows = db.execute("SELECT source_id,version,record_hash,payload FROM scientific_sources ORDER BY source_id,version").fetchall()
            impacts = db.execute("SELECT impact_id,impact_hash,payload FROM scientific_impacts ORDER BY impact_id").fetchall()
        try:
            for source_id, version, record_hash, payload in rows:
                source = _decode_source(json.loads(payload))
                if source_id != source.source_id or version != source.version or record_hash != _digest(source):
                    return False
            for impact_id, impact_hash, payload in impacts:
                impact = _decode_impact(json.loads(payload))
                if impact_id != impact.impact_id or impact_hash != _digest(impact):
                    return False
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return False
        return True


def _score(level: CorpusEvidenceLevel) -> int:
    return ScientificSourceCorpus._LEVEL_RANK[level]


def _decode_source(payload: dict) -> ScientificSourceRecord:
    payload["authors"] = tuple(payload["authors"])
    for key in ("phenomenon", "findings", "limitations", "applicability", "relevant_mechanism", "ceutia_components", "implementation_implications", "validation_requirements", "client_contexts", "question_types", "risk_levels", "response_types", "contexts"):
        payload[key] = tuple(payload.get(key, ()))
    payload["source_type"] = CorpusSourceType(payload["source_type"])
    payload["evidence_level"] = CorpusEvidenceLevel(payload["evidence_level"])
    if payload.get("retrieval"):
        payload["retrieval"] = RetrievalMetadata(**payload["retrieval"])
    return ScientificSourceRecord(**payload)


def _decode_impact(payload: dict) -> ScientificImpactMap:
    for key in ("source_ids", "limitations", "mechanism", "existing_components", "contradictions_or_modifications", "missing_capabilities", "implementation_now", "integration_requirements", "tests_required", "internal_validation", "external_validation", "dependencies", "mission_queue", "assumptions", "uncertainty"):
        payload[key] = tuple(payload[key])
    payload["validation_status"] = ValidationStatus(payload["validation_status"])
    return ScientificImpactMap(**payload)


__all__ = [
    "CorpusEvidenceLevel", "CorpusSourceType", "ImpactRelation", "RetrievalMetadata",
    "ScientificImpactMap", "ScientificRelation", "ScientificSourceCorpus", "ScientificSourceRecord",
    "ValidationStatus",
]
