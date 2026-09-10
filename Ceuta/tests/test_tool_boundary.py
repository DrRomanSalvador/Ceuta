"""Regression tests for default-deny operating-system and egress controls."""

from pathlib import Path

import pytest

from app.security.enforcement import AuthorizationError
from app.security.tool_boundary import ToolBoundary


def test_filesystem_is_denied_without_explicit_root() -> None:
    with pytest.raises(AuthorizationError):
        ToolBoundary().safe_path("/tmp/ceutia")


def test_filesystem_traversal_is_denied(tmp_path: Path) -> None:
    boundary = ToolBoundary(filesystem_roots=(tmp_path / "allowed",))
    with pytest.raises(AuthorizationError):
        boundary.safe_path(tmp_path / "outside")


def test_unallowlisted_network_destination_is_denied() -> None:
    boundary = ToolBoundary(network_hosts=frozenset({"example.com"}))
    with pytest.raises(AuthorizationError):
        boundary.safe_url("https://not-example.com/")


def test_non_https_is_denied() -> None:
    boundary = ToolBoundary(network_hosts=frozenset({"example.com"}))
    with pytest.raises(AuthorizationError):
        boundary.safe_url("http://example.com/")


def test_shell_execution_is_denied() -> None:
    boundary = ToolBoundary(allowed_commands=frozenset({"echo"}))
    with pytest.raises(AuthorizationError):
        boundary.command(["sh", "-c", "echo unsafe"])


def test_unallowlisted_command_is_denied() -> None:
    boundary = ToolBoundary(allowed_commands=frozenset())
    with pytest.raises(AuthorizationError):
        boundary.command(["echo", "test"])
