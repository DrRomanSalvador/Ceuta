# CeutIA — External Security Enforcement Boundary

## STATUS

This is a protected control-plane document.

It defines controls that MUST exist outside GitHub, outside the production host, and outside the AI execution environment before CeutIA can claim external technical enforcement of its control plane.

The repository cannot enforce its own independence from a fully compromised repository administrator, hosting administrator, server root, credential authority or CI control plane.

## 1. EXTERNAL ROOT OF TRUST

The ultimate authorization root MUST be outside:

- GitHub;
- GitHub Actions;
- the production server;
- the application process;
- AI models and agents;
- agent memory;
- repository-stored credentials;
- ordinary server environment variables;
- deployment scripts controlled by the production host.

The external authority MUST be controlled by the human project owner through an independent authentication mechanism.

## 2. GITHUB COMPROMISE BOUNDARY

A compromise of GitHub, a repository credential, a maintainer credential, a CI workflow, a pull request, a branch or a GitHub administrator MUST NOT by itself authorize deployment or high-impact CeutIA actions.

Required external controls include, as applicable:

- protected `main` branch/ruleset;
- mandatory pull requests;
- mandatory CODEOWNER review;
- required security checks;
- force-push and deletion restrictions;
- restricted bypass permissions;
- signed commit/tag verification where supported;
- independent artifact admission.

If GitHub-side administration cannot be independently protected, GitHub remains a collaboration/source domain, not a root of trust.

## 3. HOST COMPROMISE BOUNDARY

A fully compromised production host, container, operating-system root account or application process MUST be treated as hostile.

The host MUST NOT contain the external private signing key.

The host MUST NOT be able to mint valid external attestations.

The host MUST NOT be able to convert its own configuration, environment, database, clock, process state or modified binary into proof of authorization.

Production execution requires independently verifiable admission evidence.

## 4. CREDENTIAL COMPROMISE BOUNDARY

Compromise of one credential domain MUST NOT automatically grant authority in another domain.

Credentials must be:

- uniquely attributable;
- least-privileged;
- short-lived where practical;
- independently revocable;
- scoped to exact capabilities;
- excluded from model context and ordinary logs.

Possession of an owner-associated credential alone MUST NOT be treated as proof of owner intent for high-impact actions.

## 5. INDEPENDENT DEPLOYMENT ADMISSION

Deployment admission MUST bind at minimum:

- authenticated owner authorization;
- exact artifact digest;
- exact protected-control-plane digest;
- policy version;
- trust key identifier;
- issuance and expiration time;
- nonce/replay protection;
- revocation state.

The production host may verify this evidence but must not create it.

## 6. EXTERNAL REVOCATION AND KILL SWITCH

Revocation MUST remain possible when GitHub, the production host, an AI agent, credentials or application state are compromised.

At minimum, the independent authority must be capable of:

1. revoking the affected authorization/key;
2. preventing new admission;
3. invalidating active credentials where technically supported;
4. preserving security evidence;
5. authorizing recovery only after independent verification.

The component being revoked cannot be the sole authority that revokes itself or declares itself recovered.

## 7. INDEPENDENT RECOVERY

Recovery artifacts and recovery authorization MUST exist outside the potentially compromised execution domain.

A compromised host must be replaceable rather than trusted merely because it has been cleaned.

Recovery MUST verify artifact identity and protected-control-plane integrity before admission.

## 8. DATA, HUMAN RIGHTS, MEDICAL AND DUAL-USE BOUNDARY

External enforcement applies not only to code integrity but also to high-impact actions involving:

- sensitive personal data;
- medical or professional decisions;
- legal commitments;
- publication or representation of the owner;
- accusations or attribution concerning identifiable persons or groups;
- financial actions;
- national-security-sensitive information;
- dual-use or conflict-related operations;
- irreversible destructive actions.

No AI output, consensus, weak signal, score, memory item or retrieved instruction may independently cross these boundaries.

## 9. CURRENT CLAIM STATUS

Until the independent external authority, independent revocation, GitHub branch/ruleset enforcement and independent recovery path are actually provisioned and verified, CeutIA MUST describe the corresponding controls as specified or policy-protected, not as externally immutable.

The absence of external enforcement is itself a security finding and MUST NOT be hidden by documentation.

## FINAL INVARIANT

**A SYSTEM CANNOT BE THE SOLE ROOT OF TRUST FOR THE CONTROLS THAT LIMIT ITS OWN AUTHORITY.**

**A COMPROMISED COMPONENT CANNOT BE THE SOLE SOURCE OF EVIDENCE THAT IT IS TRUSTWORTHY.**
