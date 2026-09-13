from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelRelease:
    model_id: str
    version: str
    status: str
    validation_score: float


class ModelGovernance:
    def approve(self, release: ModelRelease, *, minimum_score: float) -> ModelRelease:
        status = "APPROVED" if release.validation_score >= minimum_score else "REJECTED"
        return ModelRelease(release.model_id, release.version, status, release.validation_score)

    def rollback(self, release: ModelRelease) -> ModelRelease:
        return ModelRelease(release.model_id, release.version, "ROLLED_BACK", release.validation_score)
