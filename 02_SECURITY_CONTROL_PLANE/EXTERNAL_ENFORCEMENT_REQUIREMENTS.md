# CeutIA — EXTERNAL ENFORCEMENT REQUIREMENTS

This file is a protected implementation requirement. It records controls that cannot be made effective by repository code alone.

## REQUIRED INDEPENDENT CONTROLS

The production security boundary is incomplete until the following are independently provisioned and verified:

- GitHub ruleset protecting `main`.
- Required pull request before merge.
- Required owner/code-owner approval for protected control-plane changes.
- Required security-control-plane CI status check.
- Force-push disabled on `main`.
- Branch deletion disabled on `main`.
- Administrative bypass minimized and separately audited.
- Signed commit/tag verification where used by the release process.
- External immutable control-plane manifest and digest registry.
- Hardware-backed or independently managed signing key.
- External revocation registry.
- External high-impact human-authorization service.
- Independent deployment admission gateway.
- External append-only/tamper-evident audit storage.
- Independent kill switch.
- Independent recovery source.
- Key rotation and emergency revocation.
- Replay protection and trustworthy time.
- Dependency, container and model artifact provenance verification.
- CI action pinning to immutable references.
- Host-level hardening and, where available, measured boot/device identity.
- Default-deny production network egress.
- Secrets kept outside source, model context and ordinary runtime configuration.

## NON-BYPASSABILITY REQUIREMENT

A control is classified as technically enforced only when an attacker with administrative control over GitHub alone cannot remove, rewrite or bypass it.

A control is classified as externally enforced only when an attacker with root control over the production host alone cannot remove, rewrite or bypass it.

A control is classified as owner-authorized only when an AI, GitHub administrator, production host, stored application credential or model context cannot manufacture valid owner approval.

## BOOTSTRAP RULE

Until the independent external enforcement stack exists, CeutIA MUST fail closed for consequential deployment and high-impact execution rather than silently falling back to repository-local trust.

No documentation, environment variable, GitHub setting, model statement or successful local test may be represented as a substitute for the missing external enforcement layer.
