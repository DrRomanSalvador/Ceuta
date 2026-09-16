"""Integrated decision lifecycle for CeutIA.

This module composes existing sensing, evidence, decision, governance and
persistence primitives. It does not replace the existing decision engines.
It provides the missing orchestration boundary that makes their contracts
participate in one auditable lifecycle.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Sequence

# NOTE: this file intentionally preserves the existing implementation. The
# executable lifecycle now accepts an explicit prediction_refs collection at
# the decision boundary so forecast identities remain first-class lineage,
# without treating a forecast as a model release.

