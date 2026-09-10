# CeutIA External Trust Bootstrap

This is an operational specification, not a claim that an external authorization service already exists.

## Required independent components

The production deployment MUST have an authorization/attestation authority outside GitHub and outside the production host. The authority holds the private signing key. CeutIA receives only its public verification key.

Recommended separation:

- owner authenticator: independent hardware-backed authentication;
- authorization authority: separate security boundary;
- artifact/integrity verifier: independent verification path;
- production host: execution only;
- GitHub: source and collaboration only;
- Clouding: infrastructure only.

## Credentials

No private signing key may be stored in:

- GitHub repository or secrets;
- GitHub Actions runner;
- Clouding VPS;
- CeutIA environment variables;
- Docker image;
- source tree;
- AI model context;
- agent memory;
- deployment artifact;
- ordinary application configuration.

The runtime may store a public verification key or an independently authenticated key reference.

## Artifact admission

Before deployment, an external authority must verify and attest:

1. exact source commit;
2. exact build artifact digest;
3. protected control-plane digest;
4. dependency/build provenance;
5. policy version;
6. security-gate result;
7. issuance and expiry;
8. unique nonce;
9. authorization key identifier.

The production host must reject an artifact whose attestation does not match the locally measured artifact and protected control-plane state.

## GitHub compromise

If GitHub is compromised, repository content, workflows, Actions credentials, deploy keys and release metadata are considered untrusted. A GitHub compromise must not expose the external signing key or permit an attacker to mint an accepted deployment attestation.

## Clouding compromise

If Clouding or the host is compromised, the host is placed in incident state and its runtime credentials are revoked externally. Recovery uses a newly provisioned host and independently verified artifacts. The old host cannot approve its own recovery.

## Credential compromise

Compromise of an application credential must not imply compromise of the external authority. Credentials are scoped, short-lived where possible, separately revocable, and never treated as proof of owner authority.

## Owner compromise

A suspected compromise of the owner authentication path triggers external revocation and key-rotation/recovery procedures. A compromised owner session is not allowed to silently establish a new trust root.

## Network failure

If the external authority is unreachable or its attestation cannot be verified, high-impact operations and deployment admission fail closed. Availability does not override authorization integrity.

## No self-attestation

CeutIA, an agent, the production host, GitHub Actions, a model, a connector, or a CI job MUST NOT issue an attestation that it later accepts as its own root of trust.

## Recovery invariant

> A COMPROMISED COMPONENT CANNOT BE THE SOLE SOURCE OF EVIDENCE THAT IT IS NO LONGER COMPROMISED.
