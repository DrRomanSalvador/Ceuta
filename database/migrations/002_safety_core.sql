CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS policy_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    actor_id UUID,
    purpose VARCHAR(64) NOT NULL,
    decision VARCHAR(32) NOT NULL
        CHECK (
            decision IN (
                'ALLOW',
                'ALLOW_WITH_CONTROLS',
                'HUMAN_REVIEW_REQUIRED',
                'BLOCK'
            )
        ),
    risk_tier VARCHAR(16) NOT NULL
        CHECK (
            risk_tier IN (
                'LOW',
                'MODERATE',
                'HIGH',
                'CRITICAL'
            )
        ),
    findings JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_controls JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_policy_decisions_request
    ON policy_decisions(request_id);

CREATE INDEX IF NOT EXISTS idx_policy_decisions_created
    ON policy_decisions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_policy_decisions_blocked
    ON policy_decisions(decision)
    WHERE decision = 'BLOCK';


CREATE TABLE IF NOT EXISTS provenance_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    child_type VARCHAR(64) NOT NULL,
    child_id UUID NOT NULL,

    parent_type VARCHAR(64) NOT NULL,
    parent_id UUID NOT NULL,

    relation VARCHAR(64) NOT NULL,

    transformation VARCHAR(255),
    processor VARCHAR(255),
    processor_version VARCHAR(128),

    content_hash CHAR(64),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (
        child_type,
        child_id,
        parent_type,
        parent_id,
        relation
    )
);

CREATE INDEX IF NOT EXISTS idx_provenance_child
    ON provenance_links(child_type, child_id);

CREATE INDEX IF NOT EXISTS idx_provenance_parent
    ON provenance_links(parent_type, parent_id);


CREATE TABLE IF NOT EXISTS evidence_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    evidence_a UUID NOT NULL,
    evidence_b UUID NOT NULL,

    relationship VARCHAR(32) NOT NULL
        CHECK (
            relationship IN (
                'SUPPORTS',
                'CONTRADICTS',
                'DUPLICATE',
                'DERIVED_FROM',
                'DEPENDENT_ON',
                'NEUTRAL'
            )
        ),

    independence_group VARCHAR(255),

    strength NUMERIC(6,5)
        CHECK (strength >= 0 AND strength <= 1),

    rationale TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CHECK (evidence_a <> evidence_b),

    UNIQUE (
        evidence_a,
        evidence_b,
        relationship
    )
);

CREATE INDEX IF NOT EXISTS idx_evidence_rel_a
    ON evidence_relationships(evidence_a);

CREATE INDEX IF NOT EXISTS idx_evidence_rel_b
    ON evidence_relationships(evidence_b);


CREATE TABLE IF NOT EXISTS epistemic_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    claim_id UUID,

    state VARCHAR(64) NOT NULL,

    evidence_confidence NUMERIC(6,5) NOT NULL
        CHECK (evidence_confidence BETWEEN 0 AND 1),

    contradiction_ratio NUMERIC(6,5) NOT NULL
        CHECK (contradiction_ratio BETWEEN 0 AND 1),

    independent_support_groups INTEGER NOT NULL
        CHECK (independent_support_groups >= 0),

    independent_opposition_groups INTEGER NOT NULL
        CHECK (independent_opposition_groups >= 0),

    event_probability NUMERIC(6,5)
        CHECK (event_probability BETWEEN 0 AND 1),

    probability_status VARCHAR(32) NOT NULL
        CHECK (
            probability_status IN (
                'NOT_CALIBRATED',
                'CALIBRATED',
                'NOT_APPLICABLE'
            )
        ),

    uncertainty NUMERIC(6,5) NOT NULL
        CHECK (uncertainty BETWEEN 0 AND 1),

    algorithm_version VARCHAR(128) NOT NULL,
    model_version VARCHAR(128),

    explanation TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_epistemic_claim
    ON epistemic_evaluations(claim_id);


CREATE TABLE IF NOT EXISTS human_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    resource_type VARCHAR(64) NOT NULL,
    resource_id UUID NOT NULL,

    required_reviewers INTEGER NOT NULL
        CHECK (required_reviewers BETWEEN 1 AND 2),

    status VARCHAR(32) NOT NULL
        CHECK (
            status IN (
                'PENDING',
                'APPROVED',
                'REJECTED',
                'EXPIRED'
            )
        )
        DEFAULT 'PENDING',

    reviewer_ids UUID[] NOT NULL DEFAULT '{}',

    decision_reason TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_human_reviews_pending
    ON human_reviews(status)
    WHERE status = 'PENDING';

CREATE INDEX IF NOT EXISTS idx_human_reviews_resource
    ON human_reviews(resource_type, resource_id);


CREATE TABLE IF NOT EXISTS audit_chain_events (
    id UUID PRIMARY KEY,

    sequence_no BIGSERIAL UNIQUE,

    timestamp TIMESTAMPTZ NOT NULL,

    actor_id UUID,

    action VARCHAR(128) NOT NULL,

    resource_type VARCHAR(64) NOT NULL,

    resource_id UUID,

    decision VARCHAR(32),

    payload_hash CHAR(64) NOT NULL,

    previous_hash CHAR(64) NOT NULL,

    event_hash CHAR(64) NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_chain_sequence
    ON audit_chain_events(sequence_no);

CREATE INDEX IF NOT EXISTS idx_audit_resource
    ON audit_chain_events(resource_type, resource_id);


CREATE TABLE IF NOT EXISTS model_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(255) NOT NULL,

    provider VARCHAR(255),

    artifact_hash CHAR(64),

    purpose VARCHAR(64) NOT NULL,

    approval_status VARCHAR(32) NOT NULL
        CHECK (
            approval_status IN (
                'PENDING',
                'APPROVED',
                'SUSPENDED',
                'REVOKED'
            )
        )
        DEFAULT 'PENDING',

    sensitive_data_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    external_data_allowed BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(model_name, model_version)
);


CREATE OR REPLACE FUNCTION reject_uncalibrated_probability()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN

    IF NEW.probability IS NOT NULL
       AND COALESCE(
            NEW.current_evaluation ->> 'probability_status',
            'NOT_CALIBRATED'
       ) <> 'CALIBRATED'
       AND TG_TABLE_NAME = 'hypotheses'
    THEN

        RAISE EXCEPTION
            'Uncalibrated probability cannot be stored as statistical probability';

    END IF;

    RETURN NEW;

END;
$$;


DROP TRIGGER IF EXISTS hypotheses_probability_guard
    ON hypotheses;

CREATE TRIGGER hypotheses_probability_guard
BEFORE INSERT OR UPDATE
ON hypotheses
FOR EACH ROW
EXECUTE FUNCTION reject_uncalibrated_probability();


REVOKE UPDATE, DELETE
ON audit_chain_events
FROM PUBLIC;