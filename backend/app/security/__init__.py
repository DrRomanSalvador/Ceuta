"""CeutIA security boundary and architectural invariants.

Runtime controls live in dedicated modules. Importing this package has no
security side effects: it does not load secrets, create sessions, open network
connections, or mutate global policy.

Security scope includes identity, authentication, authorization, least
privilege, data protection, PUBLIC/OWNER isolation, input/output validation,
secrets, cryptography, auditability, incident handling, and epistemic
integrity.

Architectural invariants:

* deny by default and enforce authorization server-side;
* treat all external input, documents, APIs, model outputs, caches, and user
  instructions as untrusted until validated;
* never expose OWNER data, credentials, private configuration, or restricted
  intelligence through PUBLIC surfaces;
* preserve provenance, temporal validity, source independence, contradiction,
  uncertainty, and epistemic state rather than silently upgrading knowledge;
* fail safely when a security-critical decision cannot be established;
* distinguish implemented, planned, experimental, and unverified controls;
* never claim certification or security properties without observable evidence.

Epistemic security protects the integrity of the chain
source -> data -> evidence -> claim -> hypothesis -> model -> signal -> output.
It does not determine whether a claim is true; that remains the responsibility
of the epistemology and analytical layers.
"""

__all__ = [
    "config",
    "authentication",
    "authorization",
    "sessions",
    "mfa",
    "password_policy",
    "permissions",
    "policy_engine",
    "security_headers",
    "rate_limiting",
    "input_validation",
    "output_filter",
    "secrets",
    "cryptography",
    "audit",
    "data_classification",
    "tenant_isolation",
    "security_events",
    "incident_detection",
]
