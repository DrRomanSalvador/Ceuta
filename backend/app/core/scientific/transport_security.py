"""Authenticated transport primitives for canonical SERPIENTE predictions."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import secrets
import sqlite3

DEFAULT_MAX_SKEW = timedelta(minutes=5)


def canonical_transport_message(payload: dict[str, object], *, timestamp: str, nonce: str) -> bytes:
    if not timestamp or not nonce:
        raise ValueError("transport timestamp and nonce are required")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return f"{timestamp}\n{nonce}\n{canonical}".encode("utf-8")


def sign_transport(payload: dict[str, object], *, secret: str, timestamp: str, nonce: str) -> str:
    if not secret:
        raise ValueError("transport secret is required")
    return hmac.new(secret.encode("utf-8"), canonical_transport_message(payload, timestamp=timestamp, nonce=nonce), hashlib.sha256).hexdigest()


def ensure_transport_schema(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS scientific_transport_nonces (
        nonce TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        consumed_at TEXT NOT NULL
    )""")
    connection.commit()


def verify_and_consume_transport(
    connection: sqlite3.Connection,
    payload: dict[str, object],
    *,
    secret: str,
    timestamp: str,
    nonce: str,
    signature: str,
    now: datetime | None = None,
    max_skew: timedelta = DEFAULT_MAX_SKEW,
) -> None:
    if not secret:
        raise ValueError("producer transport secret is not configured")
    if not nonce or len(nonce) < 16 or len(nonce) > 200:
        raise ValueError("invalid transport nonce")
    if not signature or len(signature) != 64:
        raise ValueError("invalid transport signature")
    try:
        supplied_time = datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise ValueError("invalid transport timestamp") from exc
    if supplied_time.tzinfo is None or supplied_time.utcoffset() is None:
        raise ValueError("transport timestamp must be timezone-aware")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    supplied_time = supplied_time.astimezone(timezone.utc)
    if abs(current - supplied_time) > max_skew:
        raise ValueError("transport timestamp outside replay window")
    expected = sign_transport(payload, secret=secret, timestamp=timestamp, nonce=nonce)
    if not hmac.compare_digest(signature, expected):
        raise ValueError("transport signature verification failed")
    ensure_transport_schema(connection)
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute("SELECT nonce FROM scientific_transport_nonces WHERE nonce=?", (nonce,)).fetchone()
        if row is not None:
            raise ValueError("transport nonce has already been consumed")
        connection.execute("INSERT INTO scientific_transport_nonces(nonce,timestamp,consumed_at) VALUES(?,?,?)", (nonce, timestamp, current.isoformat()))
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def new_transport_credentials(*, now: datetime | None = None) -> tuple[str, str]:
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    return timestamp, secrets.token_urlsafe(24)


__all__ = [
    "DEFAULT_MAX_SKEW",
    "canonical_transport_message",
    "sign_transport",
    "verify_and_consume_transport",
    "new_transport_credentials",
]
