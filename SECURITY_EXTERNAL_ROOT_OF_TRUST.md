# CeutIA External Root of Trust

## Purpose

This document defines the trust boundary required to prevent compromise of GitHub, Clouding, the runtime host, application credentials, agents, models, connectors, or CI from becoming control-plane authority.

## Trust model

GitHub, Clouding, the application server, CI workers, agents, models, dependencies, memory, connectors, and runtime credentials are treated as potentially compromisable execution infrastructure. None is a root of trust.

The root of trust is external to those systems and is controlled by the sole human project owner. Its private signing material MUST NOT be stored in the repository, GitHub Actions, Clouding, the CeutIA runtime, an AI context, application configuration, or ordinary server environment variables.

## External authorization invariant

A component may request authorization but MUST NOT create, mint, approve, renew, broaden, or restore its own authorization.

The external authority MUST bind authorization to at least:

- owner identity;
- authenticated principal;
- exact action class and operation;
- exact resource and destination;
- exact data classification;
- canonical parameter digest;
- authorized artifact/control-plane version;
- issuance time and expiry;
- unique nonce/token identifier;
- policy version;
- external authorization key identifier.

Changing any materially authorized field invalidates the authorization.

## Compromise assumptions

The following must be assumed independently compromiseable:

1. GitHub account, repository, Actions runner, webhook, token, deploy key and application token.
2. Clouding account, API credential, VPS control plane, network interface and host administrator.
3. Runtime operating system, root account, containers, processes, filesystem and environment.
4. Application credentials, model credentials, connector credentials and API keys.
5. AI agent, model output, prompt context, memory, retrieved content and generated code.
6. Dependencies, packages, model artifacts, CI actions and deployment artifacts.

Compromise of one domain MUST NOT confer authority in another domain.

## Deployment admission

A deployment MUST be admitted by an independent verifier using a signed attestation. The attestation MUST identify the exact artifact and protected-control-plane state that is authorized to run.

The runtime MUST fail closed when the external attestation is absent, expired, revoked, malformed, mismatched, or unverifiable.

A runtime process MUST NOT be able to manufacture a valid attestation by changing environment variables, local configuration, repository files, clocks, application state, or its own binaries.

## Revocation

Revocation MUST be maintained outside the component being revoked. Restarting, restoring, cloning, or modifying the compromised runtime MUST NOT restore revoked authority.

## Recovery

Recovery MUST start from independently verified artifacts. A compromised host is evidence of compromise, not evidence of recovery. The compromised host MUST NOT be the sole authority that declares itself clean, recovered, or trusted.

## GitHub boundary

CODEOWNERS and CI are defense-in-depth controls. They are not the external root of trust. Repository protection SHOULD require pull requests, required security checks, code-owner review, stale-approval dismissal, restricted direct pushes, force-push/deletion protection, and no bypass for ordinary identities.

Even if GitHub is completely compromised, the attacker MUST still lack the external private key and MUST therefore be unable to mint external deployment or high-impact authorization.

## Clouding/server boundary

The production host MUST be considered replaceable. Host root MUST NOT hold the external signing key. The host may verify public attestations but MUST NOT create them.

Network access to the external authorization service MUST be narrow, authenticated, rate-limited, logged, and fail closed. The service MUST NOT expose the signing key to the runtime.

## Owner safety

Owner authentication MUST use an authenticator independent of GitHub and the production host. Recovery credentials MUST be separated from ordinary runtime credentials. Owner compromise MUST trigger external revocation and re-key procedures rather than allowing the compromised identity to silently continue.

## Security claims

The system MUST distinguish `VERIFIED`, `UNVERIFIED`, `FAILED`, `INCIDENT`, and `RECOVERING`. Successful local execution is never proof of authorization or integrity.

## Final invariant

> NO COMPONENT HOSTING OR EXECUTING CeutIA MAY BECOME THE ROOT OF TRUST FOR THE CONTROLS THAT LIMIT ITS OWN AUTHORITY.
