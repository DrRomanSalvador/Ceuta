"""Default-deny boundary for filesystem, process and network capabilities."""

from __future__ import annotations

import ipaddress
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .enforcement import AuthorizationError


class ToolBoundary:
    """Restrict dangerous primitives before they reach operating-system APIs.

    This is intentionally deny-by-default. Callers must supply explicit
    allowlists; model-provided URLs, commands and paths are never trusted.
    """

    def __init__(
        self,
        *,
        filesystem_roots: tuple[Path, ...] = (),
        network_hosts: frozenset[str] = frozenset(),
        allowed_commands: frozenset[str] = frozenset(),
    ) -> None:
        self._roots = tuple(root.resolve() for root in filesystem_roots)
        self._network_hosts = network_hosts
        self._commands = allowed_commands

    def safe_path(self, path: str | Path) -> Path:
        candidate = Path(path).expanduser().resolve(strict=False)
        if not self._roots:
            raise AuthorizationError("Filesystem access is not allowlisted")
        if not any(candidate == root or root in candidate.parents for root in self._roots):
            raise AuthorizationError("Filesystem path is outside the allowed roots")
        return candidate

    def safe_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"https"} or not parsed.hostname:
            raise AuthorizationError("Only allowlisted HTTPS destinations are permitted")
        hostname = parsed.hostname.rstrip(".").lower()
        if hostname not in self._network_hosts:
            raise AuthorizationError("Network destination is not allowlisted")
        try:
            addresses = [ipaddress.ip_address(hostname)]
        except ValueError:
            addresses = []
        if any(address.is_private or address.is_loopback or address.is_link_local for address in addresses):
            raise AuthorizationError("Private or local network destinations are denied")
        return url

    def command(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        if not argv or not argv[0]:
            raise AuthorizationError("Empty command is denied")
        executable = os.path.basename(argv[0])
        if executable not in self._commands:
            raise AuthorizationError("Command is not allowlisted")
        if any(token in {"sh", "bash", "zsh", "fish", "cmd", "powershell", "pwsh"} for token in argv):
            raise AuthorizationError("Shell indirection is denied")
        return subprocess.run(
            argv,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
            env={"PATH": "/usr/bin:/bin"},
        )
