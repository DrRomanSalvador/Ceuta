# CeutIA — PROTECTED_CORE SECURITY AUDIT

**Mission:** CIBERSEGURIDAD / MISSION-15  
**Repository:** `DrRomanSalvador/Ceuta`  
**Audited ref:** `main`  
**Audited HEAD:** `5784d2734f5b75fc740d82f5275ea5cf1936de5d`  
**Audit mode:** defensive, non-invasive  
**Protected-core modification performed:** NO

## 1. Executive classification

`POLICY-PROTECTED / TECHNICAL IMMUTABILITY NOT VERIFIED / IDENTITY MAPPING UNVERIFIED / CRYPTOGRAPHIC AUTHORIZATION NOT VERIFIED`

The repository contains substantial documented and workflow-level controls, but the evidence available to this audit does not justify the stronger claims `HUMAN_ONLY_MODIFICATION`, `CRYPTOGRAPHICALLY_VERIFIABLE`, or `ADVERSARIALLY_TESTED` for the complete PROTECTED_CORE.

## 2. Identity status

The repository owner observed through GitHub is `DrRomanSalvador`. The current CODEOWNERS file names `@drsalvadorroman-beep` for the protected control plane. The authenticated GitHub profile available to this audit is `DrRomanSalvador` and exposes `iglesiasroman@hotmail.es` through the connector.

The owner-specified authorized human emails are exactly:

- `dr.salvadorroman@gmail.com`
- `Iglesiasroman@hotmail.es`
- `Roigsa1102@gmail.com`

The available evidence establishes that the connected GitHub profile exposes `Iglesiasroman@hotmail.es`, but this alone does not establish the complete required identity mapping or human authorization chain. Verified email, GitHub account identity, MFA/2FA, recovery controls, ownership/collaborator configuration and explicit human confirmation remain required. No third identity has been added or inferred.

Status: `IDENTITY_MAPPING_UNVERIFIED`.

## 3. PROTECTED_CORE perimeter

Current repository evidence identifies a protected control-plane set including:

- `AGENTS.md`
- `AUTHORITY_HIERARCHY.md`
- `SUPREME_SECURITY_LAW.md`
- `00_GOVERNANCE/`
- `01_HUMAN_SAFETY_AND_RIGHTS/`
- `02_SECURITY_CONTROL_PLANE/`
- `03_INCIDENTS_AND_RECOVERY/`
- `.github/CODEOWNERS`
- `.github/workflows/security-control-plane.yml`
- multiple root security/authority/runtime controls referenced by CODEOWNERS

Separately, mission identity, bootstrap and multi-agent governance files can reconstruct authority and operating rules. The exact canonical immutable perimeter therefore requires explicit human declaration before a cryptographic manifest is created.

Status: `HUMAN_DECISION_REQUIRED`.

No file has been promoted into or removed from the canonical PROTECTED_CORE by this audit.

## 4. GitHub control-plane evidence

- Repository visibility: `public` — verified.
- Repository owner: `DrRomanSalvador` — verified.
- Repository admin capability of the authenticated connector: observed — verified for the connected session, but this is not evidence that an AI agent is human-authorized.
- Repository rulesets endpoint: empty (`[]`) — observed.
- `main` branch protection: not verified; the available endpoint returned `403 Resource not accessible by integration`.
- CODEOWNERS: present and protects the currently declared control plane.
- Security workflow: present as repository code.
- Security workflow run on audited HEAD: no workflow runs were returned for that commit in the prior audit; no new execution evidence has been established by this activation.
- Commit signature status: not verified by the available commit metadata.

Therefore GitHub-level technical immutability is **NOT VERIFIED**.

## 5. Existing controls that are positive but not sufficient alone

`AGENTS.md` explicitly prohibits AI modification of the protected control plane and states that repository policy alone is not cryptographic immutability.

`00_GOVERNANCE/OWNER_AUTHORITY_ROOT.md` defines human-only owner authority and explicitly requires external enforcement before claiming immutability.

`SECURITY_TECHNICAL_ENFORCEMENT_ARCHITECTURE.md` defines execution-time authorization, least privilege, no self-escalation, protected control-plane layers, tamper-evident auditing and control-effectiveness states.

`SECURITY_RUNTIME_ENFORCEMENT.md` defines fail-closed, no authority propagation and no AI control-plane modification.

`SECURITY_EXTERNAL_ROOT_OF_TRUST.md` explicitly places the root of trust outside GitHub/runtime/agents and requires an independent signing authority.

`SECURITY_EXTERNAL_TRUST_IMPLEMENTATION.md` explicitly states that the independent authority is not yet provisioned and that consequential deployment admission must remain unavailable until it is.

`SECURITY_ENFORCEMENT_TEST_PLAN.md` defines the requested adversarial test families, but a documented test plan is not evidence that all tests have executed successfully.

## 6. Workflow/supply-chain finding

`.github/workflows/security-control-plane.yml` grants `contents: read`, which is a positive least-privilege property for that workflow. However, its security-critical third-party actions use mutable major tags such as `actions/checkout@v6` and `actions/setup-python@v6` rather than immutable commit SHAs. This leaves a supply-chain integrity gap for the workflow itself.

## 7. Cryptographic integrity

Git object SHAs are useful provenance identifiers but are not a substitute for a canonical SHA-256 PROTECTED_CORE manifest and an independent trust anchor.

A complete implementation still requires:

`HUMAN_APPROVED_CORE_MANIFEST → SHA-256 FILE HASHES → DETERMINISTIC SET HASH → AUTHORIZED REVISION → EXTERNAL/INDEPENDENT ANCHOR → CONTINUOUS VERIFICATION`

Status: `CRYPTOGRAPHICALLY_VERIFIABLE = NOT YET ESTABLISHED`.

## 8. Adversarial verification matrix

| # | Scenario | Current evidence | Status |
|---|---|---|---|
| 1 | Agent with normal permissions modifies core | Policy/workflow checks exist; no execution evidence | `UNVERIFIED` |
| 2 | Agent with elevated permissions modifies core | No independent GitHub protection evidence | `UNPROTECTED` |
| 3 | Malicious PR | PR workflow detects protected paths and title gate | `DETECTED` (not independent authorization) |
| 4 | Fork attempts protected modification | No end-to-end fork enforcement test evidence | `UNVERIFIED` |
| 5 | Compromised workflow | Workflow is protected by CODEOWNERS but action refs are mutable | `UNPROTECTED` |
| 6 | Compromised dependency | Static security checks exist; complete supply-chain admission not verified | `UNVERIFIED` |
| 7 | CODEOWNERS modification | CODEOWNERS is itself protected by CODEOWNERS/workflow policy | `DETECTED` / technical enforcement not verified |
| 8 | Ruleset modification | No rulesets observed; branch protection unavailable to audit | `UNPROTECTED` |
| 9 | Hash modification | No canonical SHA-256 core manifest observed | `UNPROTECTED` |
| 10 | Manifest substitution | No independent canonical manifest/anchor verified | `UNPROTECTED` |
| 11 | Unauthorized rollback | No external authorized lineage verifier verified | `UNVERIFIED` |
| 12 | Duplicate/shadow copy | No semantic duplicate scanner verified | `UNVERIFIED` |
| 13 | Instruction override | External-data-as-data policy documented | `DETECTED` conceptually; runtime proof absent |
| 14 | Prompt injection | Test plan and runtime policy exist | `DETECTED` conceptually; runtime proof absent |
| 15 | Self-escalation | Explicit anti-self-escalation invariants exist | `DETECTED` conceptually; execution proof absent |
| 16 | Account creation | No AI account-creation authority is documented | `UNVERIFIED` operationally |
| 17 | GitHub Action modification path | Workflow is CODEOWNERS-protected; branch enforcement not verified | `UNPROTECTED` |
| 18 | Indirect modification via tool/config/dependency | Architecture prohibits it; independent action gate not verified | `UNVERIFIED` |
| 19 | Modify verifier itself | No independently protected verifier/manifest chain verified | `UNPROTECTED` |
| 20 | Alternative copy presented as canonical | No canonical semantic-authority verifier verified | `UNVERIFIED` |

## 9. Required technical closure

After explicit human declaration of the exact PROTECTED_CORE, MISSION-01 / Chat 1 should implement the executable enforcement without duplicating this mission's architecture:

1. canonical manifest and deterministic SHA-256 set hash;
2. protected verifier and manifest;
3. continuous `VERIFY_PROTECTED_CORE` gate;
4. exact-path and semantic shadow/duplicate/override detection;
5. fail-closed on verifier/manifest/policy divergence;
6. pinned immutable GitHub Action references for security-critical workflows;
7. executable tests for all 20 adversarial scenarios;
8. independent evidence collection for branch/ruleset/CODEOWNERS/identity state;
9. human-only break-glass/recovery outside agent credentials;
10. external root-of-trust integration only when an independent human-controlled authority exists.

## 10. Human decisions required

- Declare the exact canonical PROTECTED_CORE file set.
- Verify the GitHub identity corresponding to `dr.salvadorroman@gmail.com`.
- Verify the GitHub identity corresponding to `Iglesiasroman@hotmail.es`.
- Verify the GitHub identity corresponding to `Roigsa1102@gmail.com`.
- Confirm which verified GitHub identity is the authorized owner; do not infer this from repository ownership, a CODEOWNERS username, an AI session or an email alone.
- Confirm the human-only recovery/break-glass mechanism.

## 11. Security claims permitted now

Allowed:

- `PUBLIC_READABLE`
- `POLICY_PROTECTED`
- `TAMPER_EVIDENCE_DOCUMENTED`
- `FAIL_CLOSED_DOCUMENTED`
- `HUMAN_AUTHORITY_DECLARED_IN_REPOSITORY`
- `AI_MODIFICATION_PROHIBITED_BY_POLICY`

Not yet justified:

- `HUMAN_ONLY_MODIFICATION`
- `CRYPTOGRAPHICALLY_VERIFIABLE`
- `TECHNICAL_IMMUTABILITY_VERIFIED`
- `FULLY_AUDITABLE`
- `ADVERSARIALLY_TESTED`

## 12. Final invariant

`READ ≠ MODIFY`

`INVOKE ≠ ADMINISTER`

`AI ≠ HUMAN AUTHORITY`

`KNOWLEDGE ≠ MODIFICATION AUTHORITY`

`PR ≠ AUTHORIZATION`

`CODEOWNERS ≠ IMMUTABILITY`

`GITHUB ADMIN ≠ CRYPTOGRAPHIC ROOT OF TRUST`

`DOCUMENTED CONTROL ≠ ENFORCED CONTROL`

`WHEN CRITICAL VERIFICATION IS MISSING → FAIL CLOSED / HUMAN DECISION REQUIRED`
