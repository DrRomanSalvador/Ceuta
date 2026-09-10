# CeutIA External Trust Implementation Contract

The external trust layer is intentionally incomplete until an independent authority is provisioned. This repository therefore fails closed rather than silently falling back to local authority.

## Required production deployment variables

- `CEUTIA_EXTERNAL_TRUST_PUBLIC_KEY`: PEM Ed25519 public key only.
- `CEUTIA_EXTERNAL_TRUST_AUTHORITY`: stable external authority identifier.
- `CEUTIA_EXTERNAL_TRUST_KEY_ID`: active external verification-key identifier.
- `CEUTIA_POLICY_VERSION`: immutable policy version bound into attestations.

The private signing key is never a runtime variable.

## Required external service properties

The external authority must provide authenticated owner approval, short-lived signed attestations, independent revocation, key rotation, audit evidence, replay protection and recovery outside the production host.

The service must not accept authorization merely because the request originates from GitHub, Clouding, an administrator, an AI agent, a model, a local process, a stored token or a previous authorization.

## Artifact identity

The admission verifier binds an attestation to both the executable artifact digest and the deterministic digest of the protected control plane. This prevents a modified artifact from reusing an attestation issued for another artifact or policy state.

## Operational rule

Until the independent authority is provisioned and the production deployment is configured, consequential deployment admission MUST remain unavailable. There is no insecure local fallback.
