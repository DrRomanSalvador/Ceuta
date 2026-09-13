# CeutIA — CRYPTOGRAPHIC CONTROL-PLANE MANIFEST

This file defines the canonical contract for the externally signed CeutIA control-plane manifest.

## Canonical identity

The external manifest MUST identify the exact protected control-plane digest produced by the deployment verifier, the exact source commit, repository identity, policy version, manifest version, signing key identifier, issuance time, expiry, and unique nonce.

## Signature

The manifest MUST be signed outside GitHub and outside the production execution environment.

The private signing key MUST NOT be present in this repository, GitHub, CI runners, Cloud infrastructure, production hosts, containers, application processes, AI context or model memory.

## Admission

A production admission gateway MUST verify the signature and every bound field before permitting consequential execution.

Any mismatch MUST result in denial.

## Revocation

The signing key and each manifest identifier MUST be independently revocable.

Revocation state MUST be maintained outside the protected runtime and outside GitHub.

## Rotation

Key rotation MUST support an authenticated transition from an old trusted key to a new trusted key, including emergency revocation of the old key.

## Anti-rollback

The admission system MUST reject superseded or revoked manifests unless an independently authorized rollback attestation explicitly permits the exact target artifact.

## Independence invariant

The component being admitted MUST NOT be able to generate, sign, revoke or validate its own trust evidence.

## Status

This contract is repository-defined. Its cryptographic enforcement is NOT claimed to be active until an external signing authority, independent manifest store, revocation service and deployment gateway are actually provisioned and verified.
