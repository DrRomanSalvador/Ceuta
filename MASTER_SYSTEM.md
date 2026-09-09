system:
  name: Ceuta / Humanidad
  purpose: >
    Analizar riesgos sociales y tecnológicos con datos verificables,
    incertidumbre explícita y supervisión humana.

data_policy:
  accepted_sources:
    - organismos públicos y reguladores
    - estadísticas oficiales
    - tribunales y boletines oficiales
    - auditorías independientes publicadas
    - literatura científica revisada por pares
  rejected_sources:
    - datos sin fecha, origen o metodología
    - afirmaciones no verificables
    - estimaciones presentadas como hechos
  provenance_required: true
  timestamp_required: true
  source_url_required: true
  versioning_required: true

model:
  state: [capacidad, gobernanza, conciencia, riesgo, incertidumbre]
  update_equation: "x[t+1] = f(x[t], observations[t], parameters) + error[t]"
  risk_equation: "R[t] = sigmoid(weighted_indicators[t])"
  uncertainty: "bayesian_posterior_and_sensitivity_analysis"
  output:
    - score
    - confidence_interval
    - data_coverage
    - assumptions
    - sources
    - recommended_human_review

governance:
  human_approval_required: true
  independent_audit_required: true
  appeals_process_required: true
  public_change_log_required: true
  emergency_shutdown_required: true

safety:
  never_claim_certainty_about_future: true
  never_generate_unverified_official_status: true
  never_make_irreversible_decisions: true
  protect_personal_data: true
