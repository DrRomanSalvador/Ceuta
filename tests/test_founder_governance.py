import pytest

from app.missions.founder_governance import FixedPointCertificate, HandoffRecord, can_retire, validate_fixed_point_hierarchy
from app.missions.founder_domain import FounderDomainError


def handoff():
    return HandoffRecord(
        "H1", "FOUNDER", "INGENIERO", "DRAFT", "commercial decision", "engineering implementation",
        "CURRENT", "DESIRED", "repo/path", "schema delta", "code delta", (), ("test",),
        ("acceptance",), ("failure",), ("validation",), ("persistence",), "implement",
    )


def cert(scope):
    return FixedPointCertificate("C1", scope, "v1", True, True, True, True, True, True, ("evidence:1",), ())


def test_handoff_requires_canonical_order():
    h = handoff()
    h.validate()
    h = h.transition("SENT").transition("ACK").transition("ACCEPT").transition("RESULT").transition("VERIFIED")
    h.validate()
    assert h.state == "VERIFIED"


def test_handoff_cannot_skip_acknowledgement():
    with pytest.raises(FounderDomainError, match="FORBIDDEN_HANDOFF_TRANSITION"):
        handoff().transition("ACCEPT")


def test_retirement_preserves_history_and_requires_reason():
    assert can_retire("ACTIVE", history_preserved=True, replacement_or_reason="superseded by successor") is True
    with pytest.raises(FounderDomainError, match="RETIREMENT_REQUIRES_HISTORY_AND_REASON"):
        can_retire("ACTIVE", history_preserved=False, replacement_or_reason="")


def test_fixed_point_scopes_do_not_promote_local_closure_to_global_closure():
    result = validate_fixed_point_hierarchy(cert("FOUNDER_LOCAL_FIXED_POINT"), None, None)
    assert result == {"FOUNDER_LOCAL_FIXED_POINT": True, "MISSION_FIXED_POINT": False, "GLOBAL_SYSTEM_FIXED_POINT": False}
