# CeutIA — EXTREME SECURITY CONTROL MATRIX

## STATUS: PROTECTED CONTROL

This matrix defines security domains that must be addressed before CeutIA is treated as having extreme protection. A domain marked only by documentation is not technically enforced.

## CONTROL DOMAINS

1. Human owner identity — sole owner; no AI owner, successor or alternate authority.
2. Human authentication — independent authentication; re-authentication for high-impact actions.
3. Authorization — action/resource/scope/time-bound authorization checked at execution.
4. Privilege — default deny; least privilege; no privilege inheritance.
5. Agent identity — unique identities and isolated credentials.
6. Agent containment — sandbox, filesystem, process, network and resource boundaries.
7. Anti-rebellion — no self-authorization, self-escalation, persistence or authority creation.
8. Control-plane integrity — protected files, integrity anchors and independent recovery.
9. Repository protection — branch/ruleset, CODEOWNERS, required checks and restricted writes.
10. Workflow security — pinned/reviewed actions, minimal permissions and protected deployment paths.
11. Secrets — isolated, scoped, revocable and unavailable to ordinary model context.
12. Network — egress allowlisting, destination controls and segmentation.
13. Tool security — explicit capability registry, input/output validation and revocation.
14. Connector security — provider isolation and no authority inheritance from external services.
15. Prompt injection — external content never becomes trusted instruction.
16. Memory — provenance, integrity, isolation, versioning and rollback.
17. RAG — source trust classification, provenance, temporal validity and poisoning resistance.
18. Model supply chain — provenance and integrity of models, adapters and artifacts.
19. Dependency supply chain — version control, vulnerability assessment and rollback.
20. Data protection — minimization, classification, purpose limitation and access control.
21. Privacy — protection against direct and inferential disclosure.
22. Confidentiality — separate trust zones and restricted outputs.
23. Exfiltration — outbound data controls and anomaly detection.
24. Publication — separate publication capability with authorization gate.
25. External communication — draft/review/approve/send separation.
26. Medical safety — clinical firewall and qualified human decision boundary.
27. Human rights — no automated consequential action from weak signals or discriminatory proxies.
28. Legal safety — no autonomous material legal commitment or fabricated legal certainty.
29. Professional liability — machine output never silently becomes professional judgment.
30. Reputation/defamation — verified fact separated from allegation and inference.
31. Attribution — no automatic attribution of attacks or hostile activity.
32. National security — sensitive analysis separated from public outputs.
33. Dual use — defensive capability cannot automatically become offensive capability.
34. Conflict safety — no autonomous targeting, retaliation or escalation.
35. Information hazards — assess whether output increases harmful capability.
36. Owner safety — protect identity, location, routines and recovery mechanisms.
37. Financial safety — no autonomous financial commitments.
38. Destructive actions — explicit authorization and reversibility preference.
39. Resource safety — bounded CPU, memory, processes, storage, network and execution time.
40. Availability — resilience against runaway processes and denial of service.
41. Audit — tamper-evident records of consequential activity.
42. Forensics — evidence independent of the affected component.
43. Incident response — stop, contain, revoke, preserve, investigate, recover.
44. Owner compromise — dedicated restricted mode and independent recovery.
45. Kill switch — independent of the target agent.
46. Revocation — authority cannot survive revocation through alternate paths.
47. Recovery — trusted artifacts and independent verification.
48. Fail closed — uncertainty in authorization or integrity denies high-impact action.
49. Mission drift — mission language never expands authority.
50. Multi-agent cascade — one compromised agent cannot bootstrap trust in others.
51. Human-machine attribution — preserve whether content is machine-generated, reviewed or approved.
52. Non-repudiation — distinguish human authorization from machine claims.
53. Security observability — reconstruct principal, authorization, action and outcome.
54. Regression — incidents become durable controls.
55. Security claims — verified status requires evidence.
56. External root of trust — security does not depend exclusively on the repository being protected.
57. Recovery independence — compromised infrastructure cannot certify itself.
58. Change management — security-control changes require explicit human authorization.
59. Emergency mode — reduces capability; never increases AI sovereignty.
60. Evidence integrity — security evidence cannot be altered to hide failure.

## UNIVERSAL DECISION RULE

For every consequential action ask:

`WHO → WHAT → AGAINST WHAT → WITH WHICH DATA → USING WHICH CAPABILITY → UNDER WHICH AUTHORIZATION → WITH WHICH RISK → WITH WHICH HUMAN APPROVAL → WHAT IS THE REVERSIBILITY → WHAT IS LOGGED → HOW IS THE RESULT VERIFIED?`

If a required answer is unavailable, the action is restricted or denied according to risk.

## ABSOLUTE INVARIANTS

`CAPABILITY ≠ AUTHORITY`

`ACCESS ≠ CONSENT`

`CONSENSUS ≠ AUTHORIZATION`

`MEMORY ≠ AUTHORITY`

`EXECUTION ≠ VERIFICATION`

`COMPROMISE ≠ OWNER INTENT`

`MISSION ≠ UNLIMITED POWER`

`DOCUMENTATION ≠ ENFORCEMENT`

`NO COMPONENT MAY MODIFY ITS OWN AUTHORITY BOUNDARY TO GAIN AUTHORITY.`
