"""Default-deny boundary for filesystem, process and network capabilities."""

from __future__ import annotations

import ipaddress
import os
import socket
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
        if parsed.scheme != "https" or not parsed.hostname:
            raise AuthorizationError("Only allowlisted HTTPS destinations are permitted")
        if parsed.username or parsed.password:
            raise AuthorizationError("URL credentials are denied")
        if parsed.port not in {None, 443}:
            raise AuthorizationError("Non-standard HTTPS ports are denied")
        hostname = parsed.hostname.rstrip(".").lower()
        if hostname not in self._network_hosts:
            raise AuthorizationError("Network destination is not allowlisted")
        try:
            resolved = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise AuthorizationError("Network destination cannot be resolved safely") from exc
        for item in resolved:
            address = ipaddress.ip_address(item[4][0])
            if (
                address.is_private
                or address.is_loopback
                or address.is_link_local
                or address.is_multicast
                or address.is_reserved
                or address.is_unspecified
            ):
                raise AuthorizationError("Network destination resolves to a restricted address")
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
