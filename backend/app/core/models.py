"""
CEUTIA PUBLIC — Core Domain Models.

Canonical domain contracts for the epistemic, evidentiary and analytical
layers of CEUTIA PUBLIC.

This module deliberately contains Pydantic domain models only.
Persistence models, API schemas and analytical implementations belong to
higher or adjacent layers.

Canonical epistemic chain:

    source
        -> artifact
        -> observation
        -> claim / event
        -> evidence
        -> signal
        -> inference
        -> hypothesis
        -> prediction
        -> scenario
        -> alert
        -> decision
        -> outcome

The models preserve:

- provenance;
- temporal semantics;
- spatial semantics;
- uncertainty;
- source independence;
- corroboration;
- contradiction;
- epistemic status;
- analytical lineage;
- model version;
- privacy classification;
- person/system separation;
- and explicit unknown states.

No model in this module determines whether a claim is true by itself.
These are contracts for representing knowledge and uncertainty.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ============================================================================
# COMMON TYPES
# ============================================================================


Probability = Annotated[float, Field(ge=0.0, le=1.0)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]
PositiveFloat = Annotated[float, Field(gt=0.0)]
NonNegativeInt = Annotated[int, Field(ge=0)]
PositiveInt = Annotated[int, Field(gt=0)]


class DomainModel(BaseModel):
    """Base configuration shared by all CEUTIA domain models."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )


class IdentifiedModel(DomainModel):
    """Domain object with stable identity and creation timestamp."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value


class TemporalInterval(DomainModel):
    """
    Explicit temporal semantics.

    event_time:
        When the real-world event occurred.

    observation_time:
        When the system or observer observed/measured it.

    publication_time:
        When the information became publicly available.

    ingestion_time:
        When CEUTIA received the artifact.

    processing_time:
        When CEUTIA processed the artifact.
    """

    event_time: datetime | None = None
    observation_time: datetime | None = None
    publication_time: datetime | None = None
    ingestion_time: datetime | None = None
    processing_time: datetime | None = None

    effective_from: datetime | None = None
    effective_to: datetime | None = None

    @model_validator(mode="after")
    def validate_temporal_order(self) -> TemporalInterval:
        timestamps = {
            "event_time": self.event_time,
            "observation_time": self.observation_time,
            "publication_time": self.publication_time,
            "ingestion_time": self.ingestion_time,
            "processing_time": self.processing_time,
        }

        for name, timestamp in timestamps.items():
            if timestamp is not None and (
                timestamp.tzinfo is None or timestamp.utcoffset() is None
            ):
                raise ValueError(f"{name} must be timezone-aware")

        if self.effective_from and self.effective_to:
            if self.effective_to <= self.effective_from:
                raise ValueError("effective_to must be later than effective_from")

        return self


class SpatialReference(DomainModel):
    """
    Spatial semantics.

    A location may be represented at different resolutions.
    Exact coordinates are deliberately optional and should not be used
    unless necessary for the declared purpose.
    """

    place_id: str | None = None
    name: str | None = None
    administrative_level: str | None = None
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    spatial_resolution_m: NonNegativeFloat | None = None

    @model_validator(mode="after")
    def validate_coordinates(self) -> SpatialReference:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")

        return self


# ============================================================================
# CLASSIFICATION
# ============================================================================


class SensitivityClass(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"
    HIGHLY_RESTRICTED = "HIGHLY_RESTRICTED"


class DataSubjectClass(StrEnum):
    SYSTEM = "SYSTEM"
    AGGREGATE = "AGGREGATE"
    PERSON = "PERSON"
    UNKNOWN = "UNKNOWN"


class EpistemicStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    REPORTED = "REPORTED"
    CORROBORATED = "CORROBORATED"
    CONTRADICTED = "CONTRADICTED"
    INFERRED = "INFERRED"
    HYPOTHESIZED = "HYPOTHESIZED"
    PREDICTED = "PREDICTED"
    SCENARIO = "SCENARIO"
    DECIDED = "DECIDED"
    OUTCOME = "OUTCOME"


class EvidenceDirection(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    NEUTRAL = "NEUTRAL"
    CONTEXTUALIZES = "CONTEXTUALIZES"
    UNKNOWN = "UNKNOWN"


class SourceType(StrEnum):
    PRIMARY_INSTITUTIONAL = "PRIMARY_INSTITUTIONAL"
    SCIENTIFIC = "SCIENTIFIC"
    PROFESSIONAL_INTERNATIONAL = "PROFESSIONAL_INTERNATIONAL"
    REPUTABLE_MEDIA = "REPUTABLE_MEDIA"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    CITIZEN_TESTIMONY = "CITIZEN_TESTIMONY"
    SENSOR = "SENSOR"
    INTERNAL_SYSTEM = "INTERNAL_SYSTEM"
    UNKNOWN = "UNKNOWN"


class SourceAuthenticity(StrEnum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


class QualityLevel(StrEnum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class UncertaintyType(StrEnum):
    MEASUREMENT = "MEASUREMENT"
    SAMPLING = "SAMPLING"
    MODEL = "MODEL"
    TEMPORAL = "TEMPORAL"
    SPATIAL = "SPATIAL"
    REPORTING = "REPORTING"
    MISSINGNESS = "MISSINGNESS"
    SOURCE = "SOURCE"
    INTERPRETATION = "INTERPRETATION"
    STRUCTURAL = "STRUCTURAL"
    UNKNOWN = "UNKNOWN"


class MissingnessMechanism(StrEnum):
    NOT_MISSING = "NOT_MISSING"
    MCAR = "MCAR"
    MAR = "MAR"
    MNAR = "MNAR"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# SOURCE
# ============================================================================


class Source(IdentifiedModel):
    """
    Origin of information.

    A source is not equivalent to an individual claim.
    Source reliability and claim validity are separate concepts.
    """

    name: str = Field(min_length=1, max_length=500)
    source_type: SourceType
    uri: str | None = None
    publisher: str | None = None

    authenticity: SourceAuthenticity = SourceAuthenticity.UNKNOWN
    quality: QualityLevel = QualityLevel.UNKNOWN

    independence_group: str | None = None

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None

    @field_validator("first_seen_at", "last_seen_at")
    @classmethod
    def validate_source_timestamps(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("source timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_source_period(self) -> Source:
        if self.first_seen_at and self.last_seen_at:
            if self.last_seen_at < self.first_seen_at:
                raise ValueError("last_seen_at cannot precede first_seen_at")
        return self


# ============================================================================
# RAW ARTIFACT
# ============================================================================


class Artifact(IdentifiedModel):
    """
    Immutable representation of an ingested information artifact.

    Examples:
    - document;
    - dataset;
    - API response;
    - image;
    - video;
    - social-media publication;
    - citizen report.
    """

    source_id: UUID

    artifact_type: str = Field(min_length=1, max_length=100)
    content_hash: str = Field(min_length=1, max_length=256)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    language: str | None = Field(default=None, max_length=20)
    mime_type: str | None = Field(default=None, max_length=200)

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC
    subject_class: DataSubjectClass = DataSubjectClass.UNKNOWN

    integrity_verified: bool = False


# ============================================================================
# OBSERVATION / MEASUREMENT
# ============================================================================


class MeasurementUncertainty(DomainModel):
    """Explicit representation of measurement uncertainty."""

    uncertainty_type: UncertaintyType
    standard_error: NonNegativeFloat | None = None
    confidence_interval_lower: float | None = None
    confidence_interval_upper: float | None = None
    relative_uncertainty: NonNegativeFloat | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> MeasurementUncertainty:
        lower = self.confidence_interval_lower
        upper = self.confidence_interval_upper

        if (lower is None) != (upper is None):
            raise ValueError(
                "confidence_interval_lower and confidence_interval_upper "
                "must be supplied together"
            )

        if lower is not None and upper is not None and upper < lower:
            raise ValueError(
                "confidence_interval_upper must be greater than or equal "
                "to confidence_interval_lower"
            )

        return self


class Observation(IdentifiedModel):
    """
    Structured observation extracted from an artifact or direct sensor.

    An observation describes what was observed, not what it means.
    """

    artifact_id: UUID
    variable: str = Field(min_length=1, max_length=300)

    value: float | int | str | bool | None = None
    unit: str | None = Field(default=None, max_length=100)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    uncertainty: MeasurementUncertainty | None = None

    missingness: MissingnessMechanism = MissingnessMechanism.NOT_MISSING

    quality: QualityLevel = QualityLevel.UNKNOWN

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    @model_validator(mode="after")
    def validate_observation(self) -> Observation:
        if (
            self.missingness == MissingnessMechanism.NOT_MISSING
            and self.value is None
        ):
            raise ValueError(
                "value cannot be None when missingness is NOT_MISSING"
            )

        return self


# ============================================================================
# EVENT
# ============================================================================


class Event(IdentifiedModel):
    """
    Representation of an event believed to have occurred.

    Event existence and event interpretation are kept separate.
    """

    event_type: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)

    temporal: TemporalInterval
    spatial: SpatialReference | None = None

    source_ids: list[UUID] = Field(default_factory=list)
    observation_ids: list[UUID] = Field(default_factory=list)

    epistemic_status: EpistemicStatus = EpistemicStatus.REPORTED
    confidence: Probability | None = None

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC


# ============================================================================
# CLAIM
# ============================================================================


class Claim(IdentifiedModel):
    """
    Atomic proposition represented by CEUTIA.

    A claim can be supported, contradicted or left unresolved.
    """

    statement: str = Field(min_length=1, max_length=5000)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    source_ids: list[UUID] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)

    epistemic_status: EpistemicStatus = EpistemicStatus.UNKNOWN

    confidence: Probability | None = None

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    @model_validator(mode="after")
    def validate_confidence(self) -> Claim:
        if self.epistemic_status == EpistemicStatus.UNKNOWN and self.confidence is not None:
            raise ValueError(
                "UNKNOWN claims should not carry a resolved confidence value"
            )

        return self


# ============================================================================
# EVIDENCE
# ============================================================================


class Evidence(DomainModel):
    """
    Relationship between an evidentiary object and a claim.

    Evidence does not become stronger merely because more sources repeat it.
    Source independence must be represented explicitly.
    """

    id: UUID = Field(default_factory=uuid4)

    claim_id: UUID
    source_id: UUID

    direction: EvidenceDirection = EvidenceDirection.UNKNOWN
    quality: QualityLevel = QualityLevel.UNKNOWN

    reliability: Probability | None = None
    independence_group: str | None = None

    description: str | None = Field(default=None, max_length=5000)

    artifact_id: UUID | None = None
    observation_id: UUID | None = None

    uncertainty: MeasurementUncertainty | None = None

    @model_validator(mode="after")
    def validate_evidence_origin(self) -> Evidence:
        if self.artifact_id is None and self.observation_id is None:
            raise ValueError(
                "evidence must reference at least one artifact or observation"
            )

        return self


class EvidenceBundle(IdentifiedModel):
    """
    Group of evidence items used to evaluate a claim.

    The bundle preserves both supporting and contradictory evidence.
    """

    claim_id: UUID
    evidence_ids: list[UUID] = Field(default_factory=list)

    supporting_count: NonNegativeInt = 0
    refuting_count: NonNegativeInt = 0

    independent_source_groups: list[str] = Field(default_factory=list)

    contradiction_present: bool = False

    aggregate_confidence: Probability | None = None

    @model_validator(mode="after")
    def validate_bundle(self) -> EvidenceBundle:
        if (
            self.supporting_count == 0
            and self.refuting_count == 0
            and self.evidence_ids
        ):
            raise ValueError(
                "evidence counts cannot both be zero when evidence exists"
            )

        return self


# ============================================================================
# PROVENANCE
# ============================================================================


class ProvenanceLinkType(StrEnum):
    DERIVED_FROM = "DERIVED_FROM"
    OBSERVED_FROM = "OBSERVED_FROM"
    PUBLISHED_BY = "PUBLISHED_BY"
    CORROBORATES = "CORROBORATES"
    CONTRADICTS = "CONTRADICTS"
    INFORMS = "INFORMS"
    GENERATED_BY = "GENERATED_BY"
    VALIDATED_BY = "VALIDATED_BY"
    SUPERSEDES = "SUPERSEDES"


class ProvenanceLink(DomainModel):
    """
    Directed provenance edge between domain objects.
    """

    source_id: UUID
    target_id: UUID
    relation: ProvenanceLinkType

    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value


class ProvenanceGraph(DomainModel):
    """
    Explicit lineage graph for an analytical object.
    """

    links: list[ProvenanceLink] = Field(default_factory=list)

    root_ids: list[UUID] = Field(default_factory=list)
    terminal_ids: list[UUID] = Field(default_factory=list)


# ============================================================================
# SIGNAL
# ============================================================================


class SignalType(StrEnum):
    ANOMALY = "ANOMALY"
    TREND = "TREND"
    ACCELERATION = "ACCELERATION"
    CHANGE_POINT = "CHANGE_POINT"
    PERSISTENCE = "PERSISTENCE"
    COUPLING = "COUPLING"
    DECOUPLING = "DECOUPLING"
    SYNCHRONIZATION = "SYNCHRONIZATION"
    PROPAGATION = "PROPAGATION"
    CAPACITY_STRESS = "CAPACITY_STRESS"
    THRESHOLD_PROXIMITY = "THRESHOLD_PROXIMITY"
    CASCADE = "CASCADE"
    WEAK_SIGNAL = "WEAK_SIGNAL"
    CONTRADICTION = "CONTRADICTION"
    INFORMATION = "INFORMATION"
    UNKNOWN = "UNKNOWN"


class Signal(IdentifiedModel):
    """
    Analytical signal extracted from observations and/or evidence.

    A signal is not automatically an alert.
    """

    signal_type: SignalType
    name: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=5000)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    source_ids: list[UUID] = Field(default_factory=list)
    observation_ids: list[UUID] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)

    strength: Probability | None = None
    persistence: NonNegativeFloat | None = None
    uncertainty: Probability | None = None

    variables: list[str] = Field(default_factory=list)

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC


# ============================================================================
# DYNAMIC STATE
# ============================================================================


class DynamicState(IdentifiedModel):
    """
    Snapshot of a system variable or multidimensional system state.
    """

    variable: str = Field(min_length=1, max_length=300)

    value: float
    baseline: float | None = None

    rate_of_change: float | None = None
    acceleration: float | None = None

    reserve: Probability | None = None
    pressure: Probability | None = None

    temporal: TemporalInterval
    spatial: SpatialReference | None = None

    uncertainty: Probability | None = None


# ============================================================================
# CAPACITY
# ============================================================================


class CapacityState(IdentifiedModel):
    """
    Capacity representation.

    Global capacity is not necessarily effective capacity, and effective
    capacity is not necessarily accessible capacity.
    """

    subsystem: str = Field(min_length=1, max_length=300)

    global_capacity: NonNegativeFloat | None = None
    effective_capacity: NonNegativeFloat | None = None
    accessible_capacity: NonNegativeFloat | None = None

    current_load: NonNegativeFloat | None = None
    arrival_rate: NonNegativeFloat | None = None
    service_rate: NonNegativeFloat | None = None

    queue_length: NonNegativeFloat | None = None
    waiting_time: NonNegativeFloat | None = None

    utilization: NonNegativeFloat | None = None

    temporal: TemporalInterval
    spatial: SpatialReference | None = None

    @field_validator("utilization")
    @classmethod
    def validate_utilization(cls, value: float | None) -> float | None:
        if value is not None and value > 1.0:
            raise ValueError("utilization must be between 0 and 1")
        return value


# ============================================================================
# INFERENCE
# ============================================================================


class Inference(IdentifiedModel):
    """
    Explicit analytical inference.

    Inference is separated from raw observation and from hypothesis.
    """

    statement: str = Field(min_length=1, max_length=5000)

    input_ids: list[UUID] = Field(default_factory=list)

    confidence: Probability | None = None
    uncertainty: Probability | None = None

    method: str = Field(min_length=1, max_length=300)
    model_version: str | None = Field(default=None, max_length=200)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC


# ============================================================================
# HYPOTHESIS COMPETITION
# ============================================================================


class HypothesisStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPPORTED = "SUPPORTED"
    WEAKENED = "WEAKENED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    SUPERSEDED = "SUPERSEDED"


class Hypothesis(IdentifiedModel):
    """
    Falsifiable explanatory hypothesis.

    Multiple hypotheses may coexist for the same observed phenomenon.
    """

    statement: str = Field(min_length=1, max_length=5000)

    status: HypothesisStatus = HypothesisStatus.ACTIVE

    prior_probability: Probability | None = None
    posterior_probability: Probability | None = None

    supporting_evidence_ids: list[UUID] = Field(default_factory=list)
    refuting_evidence_ids: list[UUID] = Field(default_factory=list)

    discriminating_predictions: list[str] = Field(default_factory=list)

    falsification_criteria: list[str] = Field(default_factory=list)

    model_version: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validate_probabilities(self) -> Hypothesis:
        if (
            self.prior_probability is not None
            and self.posterior_probability is not None
        ):
            if (
                self.posterior_probability == 0.0
                and self.status == HypothesisStatus.ACTIVE
            ):
                raise ValueError(
                    "an active hypothesis cannot have zero posterior probability"
                )

        return self


class HypothesisCompetition(IdentifiedModel):
    """
    Explicit set of competing hypotheses for one analytical question.
    """

    question: str = Field(min_length=1, max_length=5000)

    hypothesis_ids: list[UUID] = Field(min_length=1)

    selected_hypothesis_id: UUID | None = None

    @model_validator(mode="after")
    def validate_selection(self) -> HypothesisCompetition:
        if (
            self.selected_hypothesis_id is not None
            and self.selected_hypothesis_id not in self.hypothesis_ids
        ):
            raise ValueError(
                "selected_hypothesis_id must belong to hypothesis_ids"
            )

        return self


# ============================================================================
# PREDICTION
# ============================================================================


class PredictionStatus(StrEnum):
    OPEN = "OPEN"
    CONFIRMED = "CONFIRMED"
    PARTIALLY_CONFIRMED = "PARTIALLY_CONFIRMED"
    DISCONFIRMED = "DISCONFIRMED"
    EXPIRED = "EXPIRED"


class Prediction(IdentifiedModel):
    """
    Time-bounded prediction registered before its outcome is known.

    Predictions must remain available for retrospective calibration.
    """

    statement: str = Field(min_length=1, max_length=5000)

    probability: Probability

    target_time: datetime
    evaluation_window_start: datetime | None = None
    evaluation_window_end: datetime | None = None

    basis_ids: list[UUID] = Field(default_factory=list)

    model_version: str | None = Field(default=None, max_length=200)

    status: PredictionStatus = PredictionStatus.OPEN

    outcome_id: UUID | None = None

    @field_validator("target_time")
    @classmethod
    def validate_target_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("target_time must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_evaluation_window(self) -> Prediction:
        if (
            self.evaluation_window_start is not None
            and self.evaluation_window_end is not None
            and self.evaluation_window_end <= self.evaluation_window_start
        ):
            raise ValueError(
                "evaluation_window_end must be later than evaluation_window_start"
            )

        return self


# ============================================================================
# SCENARIO
# ============================================================================


class ScenarioType(StrEnum):
    BASELINE = "BASELINE"
    ADVERSE = "ADVERSE"
    FAVOURABLE = "FAVOURABLE"
    SHOCK = "SHOCK"
    CASCADE = "CASCADE"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    UNKNOWN = "UNKNOWN"


class Scenario(IdentifiedModel):
    """
    Conditional representation of a possible future system trajectory.

    A scenario is not a prediction unless explicitly represented as one.
    """

    name: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=10000)

    scenario_type: ScenarioType

    assumptions: list[str] = Field(default_factory=list)
    trigger_conditions: list[str] = Field(default_factory=list)

    probability: Probability | None = None

    horizon_start: datetime | None = None
    horizon_end: datetime | None = None

    input_ids: list[UUID] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_horizon(self) -> Scenario:
        if (
            self.horizon_start is not None
            and self.horizon_end is not None
            and self.horizon_end <= self.horizon_start
        ):
            raise ValueError("horizon_end must be later than horizon_start")

        return self


# ============================================================================
# ALERT
# ============================================================================


class AlertType(StrEnum):
    HEALTH = "HEALTH"
    PSYCHOSOCIAL = "PSYCHOSOCIAL"
    VIOLENCE_ESCALATION = "VIOLENCE_ESCALATION"
    INFORMATION = "INFORMATION"
    ENVIRONMENT = "ENVIRONMENT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    INSTITUTIONAL = "INSTITUTIONAL"
    MIGRATION_HUMANITARIAN = "MIGRATION_HUMANITARIAN"
    MULTISYSTEM = "MULTISYSTEM"


class AlertLevel(StrEnum):
    LEVEL_0 = "LEVEL_0"
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"
    LEVEL_5 = "LEVEL_5"


class AlertStatus(StrEnum):
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    ESCALATED = "ESCALATED"
    DISMISSED = "DISMISSED"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


class Alert(IdentifiedModel):
    """
    Qualified system alert.

    CEUTIA PUBLIC generates analytical alerts.
    Human review determines whether and how an alert should be escalated.

    An alert does not itself constitute an autonomous security decision.
    """

    alert_type: AlertType
    level: AlertLevel

    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=10000)

    status: AlertStatus = AlertStatus.PROPOSED

    signal_ids: list[UUID] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)
    hypothesis_ids: list[UUID] = Field(default_factory=list)

    temporal: TemporalInterval = Field(default_factory=TemporalInterval)
    spatial: SpatialReference | None = None

    probability: Probability | None = None
    uncertainty: Probability | None = None

    severity: NonNegativeInt | None = Field(default=None, le=5)
    urgency: NonNegativeInt | None = Field(default=None, le=5)

    human_review_required: bool = True
    human_review_completed: bool = False

    recommended_action: str | None = Field(default=None, max_length=5000)

    subject_class: DataSubjectClass = DataSubjectClass.SYSTEM
    sensitivity: SensitivityClass = SensitivityClass.PUBLIC

    @model_validator(mode="after")
    def validate_review_state(self) -> Alert:
        if self.human_review_completed and not self.human_review_required:
            return self

        if self.status in {
            AlertStatus.CONFIRMED,
            AlertStatus.ESCALATED,
        } and not self.human_review_completed:
            raise ValueError(
                "confirmed or escalated alerts require completed human review"
            )

        return self


# ============================================================================
# DECISION
# ============================================================================


class Decision(IdentifiedModel):
    """
    Human or institutionally authorized decision resulting from an alert,
    analytical finding or other evidence.

    CEUTIA records decisions; it does not silently turn analytical output
    into an autonomous institutional decision.
    """

    statement: str = Field(min_length=1, max_length=10000)

    basis_ids: list[UUID] = Field(default_factory=list)
    alert_ids: list[UUID] = Field(default_factory=list)

    decision_maker: str = Field(min_length=1, max_length=500)

    decision_time: datetime

    rationale: str | None = Field(default=None, max_length=10000)

    @field_validator("decision_time")
    @classmethod
    def validate_decision_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("decision_time must be timezone-aware")
        return value


# ============================================================================
# OUTCOME
# ============================================================================


class Outcome(IdentifiedModel):
    """
    Observed result used to evaluate predictions and decisions.
    """

    description: str = Field(min_length=1, max_length=10000)

    observed_at: datetime

    source_ids: list[UUID] = Field(default_factory=list)
    observation_ids: list[UUID] = Field(default_factory=list)

    matches_prediction: bool | None = None

    evaluation_confidence: Probability | None = None

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value


# ============================================================================
# MODEL / ANALYTICAL LINEAGE
# ============================================================================


class ModelExecution(IdentifiedModel):
    """
    Record of an analytical model execution.

    The execution record is required for reproducibility and retrospective
    evaluation of predictions.
    """

    model_name: str = Field(min_length=1, max_length=300)
    model_version: str = Field(min_length=1, max_length=200)

    input_ids: list[UUID] = Field(default_factory=list)
    output_ids: list[UUID] = Field(default_factory=list)

    executed_at: datetime

    code_version: str | None = Field(default=None, max_length=200)
    configuration_hash: str | None = Field(default=None, max_length=256)

    deterministic: bool = False

    @field_validator("executed_at")
    @classmethod
    def validate_executed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("executed_at must be timezone-aware")
        return value


# ============================================================================
# PERSON / SYSTEM SEPARATION
# ============================================================================


class AnalyticalSubject(StrEnum):
    SYSTEM = "SYSTEM"
    AGGREGATE = "AGGREGATE"
    PERSON = "PERSON"


class PersonSystemBoundary(DomainModel):
    """
    Explicit declaration of the analytical boundary of an object.

    Person-level information must not silently enter territorial/system
    intelligence as an identifiable individual-level signal.
    """

    subject: AnalyticalSubject

    privacy_preserving_aggregation: bool = False

    aggregation_group: str | None = None

    @model_validator(mode="after")
    def validate_boundary(self) -> PersonSystemBoundary:
        if (
            self.subject == AnalyticalSubject.SYSTEM
            and self.privacy_preserving_aggregation
        ):
            raise ValueError(
                "system-level objects cannot declare person aggregation"
            )

        if self.subject == AnalyticalSubject.AGGREGATE:
            if not self.privacy_preserving_aggregation:
                raise ValueError(
                    "aggregate analytical objects require privacy-preserving "
                    "aggregation to be explicitly declared"
                )

            if not self.aggregation_group:
                raise ValueError(
                    "aggregate objects require an aggregation_group"
                )

        return self


# ============================================================================
# UNKNOWN / DATA QUALITY
# ============================================================================


class DataQualityGate(StrEnum):
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_WARNING = "ACCEPT_WITH_WARNING"
    QUARANTINE = "QUARANTINE"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class DataQualityAssessment(DomainModel):
    """
    Quality gate applied before information enters analytical processing.
    """

    gate: DataQualityGate

    completeness: Probability | None = None
    consistency: Probability | None = None
    validity: Probability | None = None
    timeliness: Probability | None = None

    issues: list[str] = Field(default_factory=list)

    assessed_at: datetime

    @field_validator("assessed_at")
    @classmethod
    def validate_assessed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("assessed_at must be timezone-aware")
        return value


# ============================================================================
# CANONICAL DOMAIN ENVELOPE
# ============================================================================


class EpistemicObjectType(StrEnum):
    SOURCE = "SOURCE"
    ARTIFACT = "ARTIFACT"
    OBSERVATION = "OBSERVATION"
    EVENT = "EVENT"
    CLAIM = "CLAIM"
    EVIDENCE = "EVIDENCE"
    EVIDENCE_BUNDLE = "EVIDENCE_BUNDLE"
    SIGNAL = "SIGNAL"
    DYNAMIC_STATE = "DYNAMIC_STATE"
    CAPACITY_STATE = "CAPACITY_STATE"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    PREDICTION = "PREDICTION"
    SCENARIO = "SCENARIO"
    ALERT = "ALERT"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"


class EpistemicEnvelope(IdentifiedModel):
    """
    Lightweight canonical envelope for cross-layer references.

    The envelope allows pipelines to refer to heterogeneous epistemic
    objects without collapsing their semantic distinctions.
    """

    object_type: EpistemicObjectType
    object_id: UUID

    epistemic_status: EpistemicStatus = EpistemicStatus.UNKNOWN

    sensitivity: SensitivityClass = SensitivityClass.PUBLIC
    subject_class: DataSubjectClass = DataSubjectClass.UNKNOWN

    provenance_ids: list[UUID] = Field(default_factory=list)

    uncertainty: Probability | None = None

    version: PositiveInt = 1


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================


__all__ = [
    "Alert",
    "AlertLevel",
    "AlertStatus",
    "AlertType",
    "AnalyticalSubject",
    "Artifact",
    "CapacityState",
    "Claim",
    "DataQualityAssessment",
    "DataQualityGate",
    "DataSubjectClass",
    "Decision",
    "DomainModel",
    "DynamicState",
    "EpistemicEnvelope",
    "EpistemicObjectType",
    "EpistemicStatus",
    "Evidence",
    "EvidenceBundle",
    "EvidenceDirection",
    "Event",
    "Hypothesis",
    "HypothesisCompetition",
    "HypothesisStatus",
    "Inference",
    "MeasurementUncertainty",
    "MissingnessMechanism",
    "ModelExecution",
    "Observation",
    "Outcome",
    "PersonSystemBoundary",
    "Prediction",
    "PredictionStatus",
    "ProvenanceGraph",
    "ProvenanceLink",
    "ProvenanceLinkType",
    "QualityLevel",
    "Scenario",
    "ScenarioType",
    "SensitivityClass",
    "Signal",
    "SignalType",
    "Source",
    "SourceAuthenticity",
    "SourceType",
    "SpatialReference",
    "TemporalInterval",
]