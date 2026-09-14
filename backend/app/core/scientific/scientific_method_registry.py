"""Versioned scientific method/preprocessing registry.

Methodological literature makes preprocessing, analytical method and validation
window part of the scientific object. This registry prevents a result from
being detached from the method configuration that produced it.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import sqlite3


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True, slots=True)
class ScientificMethodRelease:
    method_id: str
    version: str
    method_family: str
    preprocessing: tuple[str, ...]
    assumptions: tuple[str, ...]
    validation_window: str
    applicability_boundary: str
    source_ids: tuple[str, ...]
    code_revision: str
    configuration_hash: str

    def __post_init__(self) -> None:
        if not all((self.method_id, self.version, self.method_family, self.validation_window, self.applicability_boundary, self.code_revision, self.configuration_hash)):
            raise ValueError("scientific method release metadata is incomplete")
        if not self.source_ids:
            raise ValueError("scientific method release requires source provenance")
        if not self.assumptions:
            raise ValueError("scientific method release requires assumptions")

    @property
    def fingerprint(self) -> str:
        return sha256(_canonical(asdict(self)).encode()).hexdigest()


class ScientificMethodRegistry:
    def __init__(self, storage_path: str) -> None:
        if not storage_path:
            raise ValueError("storage_path is required")
        self.storage_path = storage_path
        with sqlite3.connect(storage_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_method_releases(
                method_id TEXT NOT NULL, version TEXT NOT NULL, payload TEXT NOT NULL,
                fingerprint TEXT NOT NULL, PRIMARY KEY(method_id, version)
            )""")

    def register(self, release: ScientificMethodRelease) -> None:
        payload = _canonical(asdict(release))
        fingerprint = sha256(payload.encode()).hexdigest()
        with sqlite3.connect(self.storage_path) as db:
            if db.execute("SELECT 1 FROM scientific_method_releases WHERE method_id=? AND version=?", (release.method_id, release.version)).fetchone():
                raise ValueError("method release already exists")
            db.execute("INSERT INTO scientific_method_releases VALUES(?,?,?,?)", (release.method_id, release.version, payload, fingerprint))

    def verify_integrity(self) -> bool:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT payload,fingerprint FROM scientific_method_releases").fetchall()
        return all(sha256(payload.encode()).hexdigest() == fingerprint for payload, fingerprint in rows)


__all__ = ["ScientificMethodRegistry", "ScientificMethodRelease"]
