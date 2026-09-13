# CeutIA — CRYPTOGRAPHIC IMMUTABILITY AND EXTERNAL ENFORCEMENT

## STATUS

This document is a protected control-plane specification.

Its purpose is to define the boundary required for CeutIA to remain trustworthy even when GitHub, GitHub administrators, CI/CD, the production host, cloud infrastructure, credentials, or an AI component are compromised.

Documentation alone does not make a system cryptographically immutable. The controls below become technically effective only when independently provisioned and verified.

## 1. INDEPENDENT ROOT OF TRUST

GitHub MUST NOT be the sole root of trust for protected CeutIA controls.

The production host MUST NOT be the sole root of trust.

An AI agent, model, workflow, connector, dependency, memory store, administrator account or repository credential MUST NOT be the root of trust for the controls that limit its own authority.

The independent root of trust MUST be outside the compromise domain of the component being protected.

## 2. CRYPTOGRAPHIC CONTROL-PLANE MANIFEST

The protected control plane MUST have a canonical manifest containing, at minimum:

- canonical path;
- exact content digest;
- repository identity;
- source commit identity;
- policy version;
- manifest version;
- signing key identifier;
- issuance time;
- expiry time where applicable;
- nonce or unique manifest identifier.

The manifest MUST be digitally signed by an external authority.

A modified protected file therefore produces a different digest and fails verification unless a separately authorized human-controlled process issues a new valid manifest.

## 3. GITHUB ADMINISTRATOR COMPROMISE

A compromised GitHub administrator MUST NOT be able to manufacture a valid external control-plane signature.

A GitHub administrator MUST NOT possess the external signing private key.

A GitHub administrator MUST NOT be able to modify the independent manifest store, signing authority, revocation authority and recovery authority as one administrative action.

GitHub branch protection and rulesets remain useful defense-in-depth controls, but they are NOT the cryptographic root of trust.

A repository state is accepted only after independent verification of its signed manifest.

## 4. SIGNED COMMITS AND RELEASES

Production artifacts SHOULD be derived only from commits/releases whose provenance can be independently verified.

Where signed Git objects are used, signatures MUST be verified against a trusted key registry outside the repository.

A valid Git signature alone MUST NOT be treated as sufficient authorization if the corresponding trusted key registry may have been compromised.

## 5. ARTIFACT ATTESTATION

A deployable artifact MUST be identified by cryptographic digest.

The external admission authority MUST bind:

`artifact_digest + source_commit + control_plane_digest + dependency_manifest + policy_version + security_gate_result + validity_window + nonce + key_id`

to a signed attestation.

Changing any security-relevant component invalidates the attestation.

## 6. ANTI-ROLLBACK

Production MUST reject artifacts older than the externally authorized minimum version when rollback is not explicitly authorized.

Rollback authorization MUST be separately signed and scoped to the exact artifact and reason.

A compromised GitHub administrator MUST NOT be able to silently restore a previously vulnerable artifact and have it accepted as current.

## 7. REVOCATION

Revocation MUST exist outside the component whose authority is being revoked.

The external revocation authority MUST support immediate invalidation of:

- signing keys;
- artifact attestations;
- owner authorization tokens;
- agent capabilities;
- deployment identities;
- compromised hosts;
- compromised connectors.

Revocation state MUST be protected against modification by the revoked component.

## 8. HUMAN OWNER AUTHORITY

The sole human owner remains the project authority within the higher-priority boundaries of law, fundamental rights, professional duties and safety.

Human authorization for high-impact actions MUST be cryptographically distinguishable from model output, conversation text, stored memory, environment variables, GitHub administrator actions and ordinary application credentials.

A model cannot manufacture owner approval.

A GitHub administrator cannot manufacture owner approval.

A compromised production host cannot manufacture owner approval.

## 9. HIGH-IMPACT ACTION FIREWALL

The following MUST require independently verifiable authorization:

- protected control-plane changes;
- deployment admission;
- production configuration changes;
- secret access;
- publication representing CeutIA or its owner;
- legal commitments;
- financial transactions;
- clinical actions;
- highly sensitive data operations;
- destructive operations;
- external communications with material consequences;
- national-security or dual-use operations.

Consensus between AI systems MUST NOT satisfy this requirement.

## 10. SEPARATION OF DUTIES

The following authorities SHOULD be separate wherever practical:

1. code authoring;
2. code review;
3. build;
4. artifact signing;
5. deployment admission;
6. runtime execution;
7. revocation;
8. audit and forensic evidence preservation;
9. recovery.

No single compromised component should control all of these functions.

## 11. EXTERNAL AUDIT LOG

Security-relevant authorization, admission, revocation, deployment, publication and high-impact execution events MUST be copied to an external append-only or tamper-evident audit system.

The runtime MUST NOT be able to erase the authoritative external audit record.

Logs MUST preserve enough evidence to reconstruct who or what authorized an action, what exact artifact/state was involved, when it occurred, and what policy version applied.

## 12. EXTERNAL KILL SWITCH

A kill switch MUST be enforceable independently of the application process.

The kill mechanism MUST be capable of preventing further consequential execution when the runtime, host, credentials or application control plane is suspected to be compromised.

The compromised component MUST NOT be able to veto or redefine the kill operation.

## 13. HOST COMPROMISE

A fully compromised production host is considered untrusted.

Host root access MUST NOT expose the external private signing key.

Recovery MUST permit replacing the host rather than trusting forensic declarations made by the compromised host itself.

Production admission SHOULD additionally bind execution to an independently measured artifact/environment where platform capabilities permit it, such as hardware-backed device identity or measured boot.

## 14. NETWORK BOUNDARY

The external trust authority MUST authenticate the requesting workload independently.

Production egress MUST be default-deny and restricted to explicitly required destinations.

Trust-service communication SHOULD use mutually authenticated transport where supported.

DNS, routing and endpoint substitution MUST NOT allow a compromised workload to redirect authorization requests to an attacker-controlled authority.

## 15. SECRET BOUNDARY

Private signing keys MUST never be stored in:

- Git repositories;
- GitHub Actions runners;
- production application containers;
- ordinary host environment variables;
- AI prompts or context;
- model memory;
- vector databases;
- build artifacts;
- source code.

Where practical, signing operations SHOULD occur in hardware-backed or externally managed key infrastructure so the private key is never exportable to the application host.

## 16. KEY ROTATION

The external trust system MUST support controlled key rotation.

Rotation MUST identify:

- old key;
- new key;
- activation time;
- overlap period where applicable;
- revocation state;
- recovery procedure.

A compromised old key MUST be revocable without requiring cooperation from the compromised system.

## 17. TIME SECURITY

Short-lived authorization depends on trustworthy time.

Where practical, validity decisions SHOULD use an independently authenticated time source or a secure monotonic mechanism.

A compromised host MUST NOT be able to extend an expired authorization merely by altering its local clock.

## 18. SUPPLY CHAIN

Dependencies, build tools, CI actions, model artifacts, container images and external packages are untrusted inputs until provenance and integrity have been verified.

Production admission SHOULD bind dependency and model provenance to the signed artifact attestation.

Unreviewed dynamic downloads MUST NOT become trusted executable components.

## 19. AI-SPECIFIC BOUNDARY

Prompt injection, memory poisoning, retrieved instructions, tool output, model-generated code, multi-agent consensus and model self-description MUST be treated as untrusted data unless separately authorized.

No AI component may:

- create its own signing authority;
- modify the external trust policy to gain authority;
- create a replacement owner;
- disable revocation;
- suppress security evidence;
- establish hidden persistence;
- create an alternative command channel;
- declare itself trusted.

## 20. RECOVERY

Recovery MUST begin from independently verified state.

The recovery authority MUST not depend solely on the compromised GitHub organization, repository, host or application.

Recovery MUST verify:

`artifact + control_plane + dependencies + policy + trust_configuration + revocation_state`

before restoring consequential execution.

## 21. FAILURE STATES

The system MUST distinguish at least:

`TRUSTED`
`UNVERIFIED`
`REVOKED`
`COMPROMISED`
`RECOVERY_REQUIRED`

Only `TRUSTED` permits consequential execution.

Ambiguity MUST fail closed.

## 22. SECURITY CLAIM DISCIPLINE

CeutIA MUST NOT claim:

- cryptographic immutability;
- independent root of trust;
- secure deployment;
- effective revocation;
- tamper-proof audit;
- administrator-resistant protection;

unless the corresponding mechanism has actually been provisioned and independently verified.

## 23. REQUIRED EXTERNAL ENFORCEMENT STACK

The complete target boundary consists of:

`Human Owner`
`↓`
`Independent Authentication / Authorization Authority`
`↓`
`Hardware-backed or independently protected Signing Key`
`↓`
`Signed Control-Plane Manifest + Revocation Registry`
`↓`
`Independent Artifact / Environment Admission`
`↓`
`Protected Runtime Gateway`
`↓`
`CeutIA`

with independent:

`Audit`
`Kill Switch`
`Recovery`
`Key Rotation`
`Time / Replay Protection`

No component below the external trust boundary can promote itself above it.

## FINAL INVARIANTS

`CAPABILITY ≠ AUTHORITY`

`GITHUB ADMIN ≠ ROOT OF TRUST`

`SERVER ROOT ≠ ROOT OF TRUST`

`MODEL OUTPUT ≠ HUMAN AUTHORIZATION`

`CONSENSUS ≠ AUTHORIZATION`

`GIT SIGNATURE ≠ SOVEREIGN TRUST`

`EXECUTION ≠ VERIFICATION`

`RECOVERY ≠ PROOF OF NO COMPROMISE`

`DOCUMENTED CONTROL ≠ TECHNICALLY ENFORCED CONTROL`

`NO COMPONENT MAY GAIN MORE AUTHORITY BY MODIFYING THE RULES THAT LIMIT ITS AUTHORITY.`
