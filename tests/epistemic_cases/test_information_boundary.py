import pytest

from backend.app.core.decision.information_boundary import InformationBoundary, InformationVisibility


def test_owner_only_cannot_leak_to_public():
    boundary = InformationBoundary(InformationVisibility.OWNER_ONLY, "owner")
    assert not boundary.may_emit(InformationVisibility.PUBLIC)
    with pytest.raises(PermissionError):
        boundary.assert_emit(InformationVisibility.PUBLIC)


def test_restricted_can_remain_restricted_or_owner_only():
    boundary = InformationBoundary(InformationVisibility.RESTRICTED)
    assert boundary.may_emit(InformationVisibility.RESTRICTED)
    assert boundary.may_emit(InformationVisibility.OWNER_ONLY)
    assert not boundary.may_emit(InformationVisibility.PUBLIC)
