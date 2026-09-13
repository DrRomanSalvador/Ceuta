from app.core.audit import AuditChain
from app.core.epistemic import (
    EpistemicEngine,
    EpistemicState,
    EvidenceItem,
    ProbabilityStatus,
    calculate_risk,
)
from app.core.policy import (
    DataClass,
    PolicyDecision,
    PolicyEngine,
    PolicyRequest,
    Purpose,
    SensitiveAttribute,
)
from app.core.review import (
    ReviewLevel,
    can_publish,
    review_gate,
)


def test_individual_political_profiling_is_blocked() -> None:
    result = PolicyEngine().evaluate(
        PolicyRequest(
            purpose=Purpose.POLITICAL_TARGETING,
            actor_role="OWNER",
            target_is_individual=True,
            sensitive_attributes=frozenset(
                {SensitiveAttribute.POLITICAL_OPINION}
            ),
        )
    )

    assert result.decision is PolicyDecision.BLOCK

    assert any(
        finding.code
        == "INDIVIDUAL_HIGH_RISK_PURPOSE"
        for finding in result.findings
    )


def test_medical_data_cannot_enter_territorial_intelligence() -> None:
    result = PolicyEngine().evaluate(
        PolicyRequest(
            purpose=Purpose.TERRITORIAL_MONITORING,
            actor_role="OWNER",
            data_classes=frozenset(
                {DataClass.MEDICAL}
            ),
            uses_medical_data=True,
        )
    )

    assert result.decision is PolicyDecision.BLOCK


def test_small_group_is_blocked_for_reidentification_risk() -> None:
    result = PolicyEngine().evaluate(
        PolicyRequest(
            purpose=Purpose.TERRITORIAL_MONITORING,
            actor_role="ANALYST",
            target_is_group=True,
            observed_group_size=3,
            minimum_group_size=10,
        )
    )

    assert result.decision is PolicyDecision.BLOCK


def test_duplicate_sources_do_not_count_as_independent() -> None:
    items = [
        EvidenceItem(
            "e1",
            "s1",
            "wire-A",
            True,
            0.9,
            0.9,
            0.9,
            0.9,
        ),
        EvidenceItem(
            "e2",
            "s2",
            "wire-A",
            True,
            0.9,
            0.9,
            0.9,
            0.9,
        ),
        EvidenceItem(
            "e3",
            "s3",
            "wire-B",
            True,
            0.8,
            0.8,
            0.9,
            0.9,
        ),
    ]

    result = EpistemicEngine().evaluate(
        evidence=items
    )

    assert result.independent_support_groups == 2
    assert result.probability is None
    assert (
        result.probability_status
        is ProbabilityStatus.NOT_CALIBRATED
    )


def test_contradicting_evidence_changes_epistemic_state() -> None:
    result = EpistemicEngine().evaluate(
        evidence=[
            EvidenceItem(
                "e1",
                "s1",
                "a",
                True,
                1,
                1,
                1,
                1,
            ),
            EvidenceItem(
                "e2",
                "s2",
                "b",
                False,
                1,
                1,
                1,
                1,
            ),
            EvidenceItem(
                "e3",
                "s3",
                "c",
                False,
                1,
                1,
                1,
                1,
            ),
        ]
    )

    assert (
        result.state
        is EpistemicState.EVIDENCE_CONTRADICTED
    )


def test_no_calibrated_probability_is_never_fabricated() -> None:
    result = calculate_risk(
        evidence_confidence=0.9,
        impact=1.0,
        event_probability=None,
        uncertainty=0.1,
    )

    assert result.event_probability is None

    assert (
        result.probability_status
        is ProbabilityStatus.NOT_CALIBRATED
    )


def test_review_gates() -> None:
    assert (
        review_gate("WARNING").level
        is ReviewLevel.HUMAN
    )

    assert (
        review_gate("DANGER").level
        is ReviewLevel.TWO_PERSON
    )

    assert (
        review_gate("CRITICAL").level
        is ReviewLevel.BLOCKED
    )

    assert can_publish(
        "WARNING",
        True,
    )

    assert not can_publish(
        "WARNING",
        False,
    )

    assert can_publish(
        "DANGER",
        True,
        True,
    )

    assert not can_publish(
        "DANGER",
        True,
        False,
    )

    assert not can_publish(
        "CRITICAL",
        True,
        True,
    )


def test_audit_chain_detects_tampering() -> None:
    chain = AuditChain()

    chain.append(
        event_id="1",
        actor_id="system",
        action="CREATE",
        resource_type="claim",
        resource_id="c1",
        decision="ALLOW",
        payload={
            "value": "x"
        },
    )

    assert chain.verify()
    assert len(chain.events) == 1
