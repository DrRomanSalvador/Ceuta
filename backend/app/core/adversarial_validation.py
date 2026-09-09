# =============================================================================
# CEUTIA — SCIENTIFIC RED TEAM, FALSIFICATION & EPISTEMIC STRESS ENGINE
#!/usr/bin/env python3
"""🌍 Ceuta Ciudadano — Monitor de Riesgo IA"""

import os, requests, json, numpy as np
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)

CONFIG = {
    'weights': {'capability_growth': 0.25, 'incident_count': 0.20, 
                'governance_gap': 0.20, 'awareness_level': -0.15, 
                'international_cooperation': -0.20},
    'thresholds': {'green': 0.4, 'yellow': 0.6, 'orange': 0.75}
}

FUENTES = [
    {'nombre': 'UN OHCHR', 'url': 'https://www.ohchr.org/api/press-releases', 'tipo': 'OFICIAL'},
    {'nombre': 'arXiv', 'url': 'http://export.arxiv.org/api/query?search_query=all:ai', 'tipo': 'PREPRINT'},
    {'nombre': 'GitHub', 'url': 'https://api.github.com/search/repositories?q=ai', 'tipo': 'SOCIAL'}
]

def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))

def get_data():
    datos = {}
    for f in FUENTES:
        try:
            r = requests.get(f['url'], timeout=10).json()
            datos[f['nombre']] = len(r.get('items', r.get('results', [])))
        except: datos[f['nombre']] = 0
    return datos

def calculate():
    d = get_data()
    ind = {
        'capability_growth': min(d.get('GitHub',0)/1000, 1.0),
        'incident_count': min(d.get('UN OHCHR',0)/50, 1.0),
        'governance_gap': 1.0 - min(d.get('UN OHCHR',0)/100, 1.0),
        'awareness_level': min((d.get('UN OHCHR',0)+d.get('arXiv',0))/200, 1.0),
        'international_cooperation': min(d.get('GitHub',0)/2000, 1.0)
    }
    raw = sum(CONFIG['weights'][k] * ind.get(k, 0.5) for k in CONFIG['weights'])
    r = sigmoid(raw)
    n = len(ind)
    se = np.sqrt(r*(1-r)/n) if n>=2 else 0.5
    ci = [max(0,r-1.96*se), min(1,r+1.96*se)]
    lv = 'GREEN' if r<CONFIG['thresholds']['green'] else 'YELLOW' if r<CONFIG['thresholds']['yellow'] else 'ORANGE' if r<CONFIG['thresholds']['orange'] else 'RED'
    return {'risk': round(r,4), 'ci': [round(ci[0],4), round(ci[1],4)], 'level': lv, 'indicators': ind, 'ts': datetime.utcnow().isoformat()+'Z'}

@app.route('/')
def home():
    r = calculate()
    html = f"""<!DOCTYPE html><html><head><title>🌍 Ceuta</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font-family:sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:2rem;margin:0}}.c{{max-width:600px;margin:0 auto}}.k{{background:rgba(255,255,255,.1);border-radius:15px;padding:2rem;margin:1.5rem 0}}.r{{font-size:4rem;font-weight:bold;text-align:center}}.g{{color:#27ae60}}.y{{color:#f39c12}}.o{{color:#e67e22}}.red{{color:#e74c3c}}.l{{text-align:center;font-size:1.5rem}}.f{{font-size:.8rem;opacity:.6;text-align:center;margin-top:2rem}}</style></head>
<body><div class="c"><h1>🌍 Ceuta Ciudadano</h1>
<div class="k"><h2>Riesgo</h2><div class="r {r['level'].lower()}">{r['risk']:.2f}</div><div class="l">{r['level']}</div><div class="l">IC 95%: [{r['ci'][0]:.2f},{r['ci'][1]:.2f}]</div></div>
<div class="k"><h2>Fuentes</h2>{"".join(f"<div><strong>{f['nombre']}</strong> ({f['tipo']})<br><small>{f['url'][:60]}...</small></div><br>" for f in FUENTES)}</div>
<div class="k"><h2>Verificar</h2><ol><li>¿Fuente oficial?</li><li>¿Múltiples fuentes?</li><li>¿Fecha reciente?</li><li>¿Evidencia?</li></ol></div>
<div class="f">Actualizado: {r['ts']}<br>Clouding.OI</div></div></body></html>"""
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GeographicProxyStatus(str, Enum):
    NO_PROXY_EVIDENCE = "NO_PROXY_EVIDENCE"
    PROXY_RISK = "PROXY_RISK"
    PROXY_UNRESOLVED = "PROXY_UNRESOLVED"


@dataclass(frozen=True, slots=True)
class GeographicProxyTest:
    status: GeographicProxyStatus

    geographic_to_composition: Optional[float]
    geographic_to_outcome: Optional[float]
    geographic_to_outcome_controlling_composition: Optional[float]

    composition_to_outcome: Optional[float]

    geographic_ablation_delta: Optional[float]

    spatial_stability: Optional[float]
    temporal_stability: Optional[float]

    resolution_sensitivity: Optional[float]

    explanation: str


def evaluate_geographic_proxy(
    *,
    geographic_to_composition: Optional[float],
    geographic_to_outcome: Optional[float],
    geographic_to_outcome_controlling_composition: Optional[float],
    composition_to_outcome: Optional[float],
    geographic_ablation_delta: Optional[float],
    spatial_stability: Optional[float],
    temporal_stability: Optional[float],
    resolution_sensitivity: Optional[float],
) -> GeographicProxyTest:

    required = (
        geographic_to_composition,
        geographic_to_outcome,
        geographic_to_outcome_controlling_composition,
        composition_to_outcome,
        geographic_ablation_delta,
        spatial_stability,
        temporal_stability,
        resolution_sensitivity,
    )

    if any(value is None for value in required):
        return GeographicProxyTest(
            status=GeographicProxyStatus.PROXY_UNRESOLVED,
            geographic_to_composition=geographic_to_composition,
            geographic_to_outcome=geographic_to_outcome,
            geographic_to_outcome_controlling_composition=(
                geographic_to_outcome_controlling_composition
            ),
            composition_to_outcome=composition_to_outcome,
            geographic_ablation_delta=geographic_ablation_delta,
            spatial_stability=spatial_stability,
            temporal_stability=temporal_stability,
            resolution_sensitivity=resolution_sensitivity,
            explanation=(
                "Insufficient tests to determine whether the geographic "
                "signal acts as a proxy for population composition."
            ),
        )

    proxy_signal = (
        abs(geographic_to_composition)
        > abs(geographic_to_outcome_controlling_composition)
        and abs(geographic_ablation_delta) < 0.10
    )

    unstable = (
        spatial_stability < 0.50
        or temporal_stability < 0.50
        or resolution_sensitivity > 0.50
    )

    if proxy_signal:
        status = GeographicProxyStatus.PROXY_RISK

        explanation = (
            "The geographic variable retains a strong relationship with "
            "composition while adding limited independent explanatory "
            "information for the outcome. The geographic signal must not "
            "be promoted as a substantive tension or risk variable."
        )

    elif unstable:
        status = GeographicProxyStatus.PROXY_UNRESOLVED

        explanation = (
            "The geographic signal is unstable across time, space or "
            "geographic resolution. Its substantive interpretation remains "
            "unresolved."
        )

    else:
        status = GeographicProxyStatus.NO_PROXY_EVIDENCE

        explanation = (
            "No proxy pattern was detected by the implemented tests. "
            "This is not evidence that no proxy exists."
        )

    return GeographicProxyTest(
        status=status,
        geographic_to_composition=geographic_to_composition,
        geographic_to_outcome=geographic_to_outcome,
        geographic_to_outcome_controlling_composition=(
            geographic_to_outcome_controlling_composition
        ),
        composition_to_outcome=composition_to_outcome,
        geographic_ablation_delta=geographic_ablation_delta,
        spatial_stability=spatial_stability,
        temporal_stability=temporal_stability,
        resolution_sensitivity=resolution_sensitivity,
        explanation=explanation,
    )
# =============================================================================
#REGLA MATEMÁTICA:

NO:

Risk = Shock × Sensitivity × Reserve⁻¹ × Coupling × Propagation

SÍ:

V_local = f(Shock, Sensitivity, Reserve)
P_propagation = g(Coupling, Network, Propagation)
T_state = h(State, Thresholds)

C_t = F(V_local, P_propagation, T_state,
        Evidence, Hypotheses, Uncertainty, Calibration)

porque vulnerabilidad local,
potencial de propagación
y cruce de umbral
son mecanismos diferentes.

# Esta capa NO demuestra que una conclusión sea verdadera.
#
# Su función es intentar encontrar condiciones bajo las cuales una conclusión:
#
#   1. deja de sostenerse;
#   2. depende de una decisión arbitraria;
#   3. depende excesivamente de una única fuente;
#   4. cambia ante pequeñas perturbaciones;
#   5. desaparece al cambiar definición, ventana, denominador o modelo;
#   6. depende de supuestos no observados;
#   7. está afectada por leakage, selección, confusión o feedback;
#   8. no puede ser falsada;
#   9. no dispone de evidencia suficiente para uso operacional;
#  10. presenta una deuda epistémica que debe permanecer explícita.
#
# PRINCIPIO CENTRAL:
#
#     sobrevivir a una prueba de falsación ≠ ser verdadero
#
# La supervivencia únicamente indica que la hipótesis/conclusión no ha sido
# refutada por ese ataque bajo las condiciones definidas.
#
# CeutIA debe aumentar su confianza únicamente cuando permanece evidencia
# independiente y metodológicamente admisible después de someter la conclusión
# a intentos explícitos de refutación.
#
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from statistics import median
from typing import Any, Final, Iterable, Mapping, Sequence


# -----------------------------------------------------------------------------
# 1. Tipología de ataques científicos
# -----------------------------------------------------------------------------


class RedTeamAttackType(str, Enum):
    """Tipos de ataque aplicables a una afirmación, modelo o alerta."""

    SOURCE_REMOVAL = "source_removal"
    SOURCE_LINEAGE = "source_lineage"
    SOURCE_INDEPENDENCE = "source_independence"

    DATA_REMOVAL = "data_removal"
    DATA_PERTURBATION = "data_perturbation"
    DATA_POISONING = "data_poisoning"
    DUPLICATION = "duplication"
    SYNTHETIC_CONTAMINATION = "synthetic_contamination"

    DEFINITION_CHANGE = "definition_change"
    DENOMINATOR_CHANGE = "denominator_change"
    UNIT_CHANGE = "unit_change"

    TEMPORAL_WINDOW = "temporal_window"
    TEMPORAL_LEAKAGE = "temporal_leakage"
    REGIME_CHANGE = "regime_change"
    OUT_OF_SAMPLE = "out_of_sample"

    SPATIAL_UNIT_CHANGE = "spatial_unit_change"
    MAUP = "maup"
    SPATIAL_DEPENDENCE = "spatial_dependence"

    MODEL_CHANGE = "model_change"
    PARAMETER_PERTURBATION = "parameter_perturbation"
    PRIOR_PERTURBATION = "prior_perturbation"
    THRESHOLD_PERTURBATION = "threshold_perturbation"

    MISSINGNESS = "missingness"
    SELECTION_BIAS = "selection_bias"
    CONFOUNDING = "confounding"
    COLLIDER_BIAS = "collider_bias"
    REVERSE_CAUSALITY = "reverse_causality"
    IMMORTAL_TIME = "immortal_time"

    BASE_RATE = "base_rate"
    RARE_EVENT = "rare_event"
    FALSE_POSITIVE_COST = "false_positive_cost"
    FALSE_NEGATIVE_COST = "false_negative_cost"

    FEEDBACK = "feedback"
    INTERVENTION_CONTAMINATION = "intervention_contamination"
    BEHAVIOURAL_RESPONSE = "behavioural_response"

    EXTREME_SCENARIO = "extreme_scenario"
    COUNTERFACTUAL = "counterfactual"
    COMPETING_HYPOTHESIS = "competing_hypothesis"

    ROBUSTNESS = "robustness"
    REPRODUCIBILITY = "reproducibility"

    PROMPT_INJECTION = "prompt_injection"
    INDIRECT_INJECTION = "indirect_injection"
    FABRICATED_EVIDENCE = "fabricated_evidence"
    AUTOMATION_BIAS = "automation_bias"
    SELF_CONFIRMATION = "self_confirmation"


class RedTeamAttackOutcome(str, Enum):
    """
    Resultado epistemológico del ataque.

    SURVIVED nunca significa TRUE.
    """

    REFUTED = "refuted"
    WEAKENED = "weakened"
    SURVIVED = "survived"
    INCONCLUSIVE = "inconclusive"
    UNTESTABLE = "untestable"
    NOT_RUN = "not_run"


class RedTeamSeverity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class RedTeamRobustnessDimension(str, Enum):
    COMPUTATIONAL = "computational"
    STATISTICAL = "statistical"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    SOURCE = "source"
    MODEL = "model"
    PARAMETER = "parameter"
    DEFINITION = "definition"
    CAUSAL = "causal"
    EPISTEMIC = "epistemic"
    OPERATIONAL = "operational"
    ADVERSARIAL = "adversarial"
    REPRODUCIBILITY = "reproducibility"


class RedTeamEvidenceDependency(str, Enum):
    INDEPENDENT = "independent"
    PARTIALLY_DEPENDENT = "partially_dependent"
    DEPENDENT = "dependent"
    UNKNOWN = "unknown"


class RedTeamDebtStatus(str, Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class RedTeamPromotionDecision(str, Enum):
    """
    Decisión final del red team.

    Esta decisión no sustituye a los gates científicos anteriores.
    """

    PASS = "pass"
    PASS_WITH_RESERVATIONS = "pass_with_reservations"
    SHADOW_ONLY = "shadow_only"
    BLOCK = "block"


# -----------------------------------------------------------------------------
# 2. Excepciones específicas
# -----------------------------------------------------------------------------


class RedTeamError(RuntimeError):
    """Error base de la capa Scientific Red Team."""


class RedTeamInputError(RedTeamError):
    """Entrada inválida o insuficiente."""


class RedTeamFalsifiabilityError(RedTeamError):
    """La afirmación o hipótesis no cumple criterios mínimos de falsabilidad."""


class RedTeamCriticalFinding(RedTeamError):
    """Se ha detectado un problema crítico incompatible con promoción."""


# -----------------------------------------------------------------------------
# 3. Crítica experta
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamExpertCritique:
    """
    Crítica externa o interna dirigida contra una afirmación.

    Una crítica NO es evidencia a favor ni en contra.
    Es un mecanismo para intentar encontrar un fallo.
    """

    critique_id: str
    claim_id: str
    expert_domain: str
    attack_type: RedTeamAttackType
    severity: RedTeamSeverity

    description: str
    proposed_refutation: str
    required_test: str

    submitted_by: str
    submitted_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    evidence_ids: tuple[str, ...] = ()
    assumptions_attacked: tuple[str, ...] = ()
    resolved: bool = False

    def validate(self) -> None:
        if not self.critique_id.strip():
            raise RedTeamInputError("critique_id no puede estar vacío")

        if not self.claim_id.strip():
            raise RedTeamInputError("claim_id no puede estar vacío")

        if not self.description.strip():
            raise RedTeamInputError("La crítica debe contener una descripción")

        if not self.proposed_refutation.strip():
            raise RedTeamInputError(
                "Toda crítica científica debe especificar cómo intentaría refutar "
                "la afirmación"
            )

        if not self.required_test.strip():
            raise RedTeamInputError(
                "Toda crítica debe definir una prueba requerida"
            )

        if self.submitted_at.tzinfo is None:
            raise RedTeamInputError(
                "submitted_at debe ser timezone-aware"
            )


# -----------------------------------------------------------------------------
# 4. Registro de una prueba de falsación
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamRefutationTest:
    test_id: str
    critique_id: str
    name: str

    criterion: str
    method: str

    outcome: RedTeamAttackOutcome
    result_summary: str

    baseline_value: float | None = None
    perturbed_value: float | None = None
    tolerance: float | None = None
    effect_size: float | None = None

    reproducible: bool = False
    execution_version: str | None = None
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.test_id.strip():
            raise RedTeamInputError("test_id no puede estar vacío")

        if not self.critique_id.strip():
            raise RedTeamInputError("critique_id no puede estar vacío")

        if not self.name.strip():
            raise RedTeamInputError("name no puede estar vacío")

        if not self.criterion.strip():
            raise RedTeamInputError("Toda prueba necesita un criterio")

        if not self.method.strip():
            raise RedTeamInputError("Toda prueba necesita un método")

        if not self.result_summary.strip():
            raise RedTeamInputError(
                "Toda prueba debe conservar el resultado observado"
            )

        if self.tolerance is not None and self.tolerance < 0:
            raise RedTeamInputError("tolerance no puede ser negativa")


# -----------------------------------------------------------------------------
# 5. Sensibilidad
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamSensitivityRun:
    run_id: str
    target_id: str
    variable: str

    baseline: float
    perturbed: float
    baseline_conclusion: str
    perturbed_conclusion: str

    absolute_change: float
    relative_change: float | None

    perturbation_fraction: float
    outcome_changed: bool

    method: str
    assumptions: tuple[str, ...] = ()

    def validate(self) -> None:
        values = (
            self.baseline,
            self.perturbed,
            self.absolute_change,
            self.perturbation_fraction,
        )

        if not all(isfinite(float(value)) for value in values):
            raise RedTeamInputError(
                f"Valores no finitos en sensitivity run '{self.run_id}'"
            )

        if self.perturbation_fraction < 0:
            raise RedTeamInputError(
                "perturbation_fraction no puede ser negativa"
            )

        if self.relative_change is not None and not isfinite(
            float(self.relative_change)
        ):
            raise RedTeamInputError(
                "relative_change debe ser finito"
            )


# -----------------------------------------------------------------------------
# 6. Robustez multidimensional
# -----------------------------------------------------------------------------


@dataclass
class RedTeamRobustnessAssessment:
    target_id: str
    scores: dict[RedTeamRobustnessDimension, float] = field(default_factory=dict)
    attack_count: int = 0
    refuted_count: int = 0
    weakened_count: int = 0
    survived_count: int = 0
    inconclusive_count: int = 0

    unresolved_major_attacks: int = 0
    unresolved_critical_attacks: int = 0

    notes: list[str] = field(default_factory=list)

    def set_score(
        self,
        dimension: RedTeamRobustnessDimension,
        score: float,
    ) -> None:
        if not isfinite(float(score)):
            raise RedTeamInputError("El score debe ser finito")

        if not 0.0 <= score <= 1.0:
            raise RedTeamInputError(
                "Los scores de robustez deben estar entre 0 y 1"
            )

        self.scores[dimension] = float(score)

    @property
    def minimum_score(self) -> float | None:
        if not self.scores:
            return None
        return min(self.scores.values())

    @property
    def mean_score(self) -> float | None:
        if not self.scores:
            return None
        return sum(self.scores.values()) / len(self.scores)


# -----------------------------------------------------------------------------
# 7. Dependencia mínima de evidencia
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamEvidenceSet:
    evidence_ids: tuple[str, ...]
    independent_source_ids: tuple[str, ...]
    conclusion_supported: bool

    removed_evidence_id: str | None = None
    conclusion_after_removal: bool | None = None

    dependency: RedTeamEvidenceDependency = (
        RedTeamEvidenceDependency.UNKNOWN
    )

    explanation: str = ""


@dataclass
class RedTeamMinimumEvidenceAnalysis:
    """
    Determina cuánto depende una conclusión de cada pieza de evidencia.

    Importante:
    un conjunto mínimo de evidencia no equivale a evidencia causal.
    """

    target_id: str
    baseline_supported: bool

    evidence_sets: list[RedTeamEvidenceSet] = field(default_factory=list)

    fragile_evidence_ids: list[str] = field(default_factory=list)
    indispensable_evidence_ids: list[str] = field(default_factory=list)

    single_source_failure: bool = False

    def validate(self) -> None:
        if not self.target_id.strip():
            raise RedTeamInputError("target_id no puede estar vacío")


# -----------------------------------------------------------------------------
# 8. Hipótesis competidoras
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamCompetingHypothesis:
    hypothesis_id: str
    target_id: str

    statement: str
    mechanism: str

    predictions: tuple[str, ...]
    discriminating_observations: tuple[str, ...]

    supporting_evidence_ids: tuple[str, ...] = ()
    contradicting_evidence_ids: tuple[str, ...] = ()

    prior_assumption: str | None = None

    def validate(self) -> None:
        if not self.statement.strip():
            raise RedTeamInputError(
                "La hipótesis debe contener una afirmación explícita"
            )

        if not self.mechanism.strip():
            raise RedTeamInputError(
                "La hipótesis debe describir un mecanismo"
            )

        if not self.predictions:
            raise RedTeamFalsifiabilityError(
                f"Hipótesis '{self.hypothesis_id}' no tiene predicciones"
            )

        if not self.discriminating_observations:
            raise RedTeamFalsifiabilityError(
                f"Hipótesis '{self.hypothesis_id}' no tiene observaciones "
                "discriminantes"
            )


# -----------------------------------------------------------------------------
# 9. Falsabilidad
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamFalsifiabilityAssessment:
    target_id: str

    falsifiable: bool

    falsification_conditions: tuple[str, ...]
    weakening_conditions: tuple[str, ...]
    inconclusive_conditions: tuple[str, ...]

    time_horizon: str | None
    observable_outcomes: tuple[str, ...]

    unfalsifiable_reason: str | None = None

    def validate(self) -> None:
        if self.falsifiable:
            if not self.falsification_conditions:
                raise RedTeamFalsifiabilityError(
                    "Una afirmación falsable debe especificar condiciones de "
                    "refutación"
                )

            if not self.observable_outcomes:
                raise RedTeamFalsifiabilityError(
                    "Una afirmación falsable necesita resultados observables"
                )

        elif not self.unfalsifiable_reason:
            raise RedTeamFalsifiabilityError(
                "Una afirmación no falsable debe explicar por qué"
            )


def validate_redteam_falsifiability(
    assessment: RedTeamFalsifiabilityAssessment,
) -> None:
    """
    Valida que una hipótesis no pueda protegerse de cualquier resultado.

    Ejemplo inválido:

        "El sistema es correcto porque cualquier observación confirma
        que el sistema tenía razón."

    Esto constituye una estructura no falsable.
    """
    assessment.validate()


# -----------------------------------------------------------------------------
# 10. Deuda epistémica
# -----------------------------------------------------------------------------


@dataclass
class RedTeamEpistemicDebtItem:
    debt_id: str
    target_id: str

    statement: str
    missing_information: str
    reason_missing: str

    resolving_data: tuple[str, ...]
    competing_hypotheses: tuple[str, ...]

    discriminating_observation: str | None

    responsible_party: str | None
    priority: int

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    reevaluation_at: datetime | None = None
    status: RedTeamDebtStatus = RedTeamDebtStatus.OPEN

    def validate(self) -> None:
        if not self.statement.strip():
            raise RedTeamInputError("La deuda epistémica necesita statement")

        if not self.missing_information.strip():
            raise RedTeamInputError(
                "Debe especificarse qué información falta"
            )

        if not self.resolving_data:
            raise RedTeamInputError(
                "Debe especificarse qué datos podrían resolver la deuda"
            )

        if self.priority < 1:
            raise RedTeamInputError(
                "priority debe ser >= 1"
            )


# -----------------------------------------------------------------------------
# 11. Feedback inducido por CeutIA
# -----------------------------------------------------------------------------


class RedTeamFeedbackDirection(str, Enum):
    NONE = "none"
    AMPLIFYING = "amplifying"
    DAMPENING = "dampening"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RedTeamFeedbackEvent:
    event_id: str
    target_id: str

    ceutia_output: str
    observed_response: str

    direction: RedTeamFeedbackDirection

    lag: float | None
    measurable: bool

    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.ceutia_output.strip():
            raise RedTeamInputError(
                "Debe registrarse la salida que pudo producir feedback"
            )

        if not self.observed_response.strip():
            raise RedTeamInputError(
                "Debe registrarse la respuesta observada"
            )

        if self.lag is not None and self.lag < 0:
            raise RedTeamInputError(
                "lag no puede ser negativo"
            )


def detect_redteam_feedback_loop(
    events: Sequence[RedTeamFeedbackEvent],
) -> RedTeamFeedbackDirection:
    """
    Clasificación conservadora de feedback.

    No infiere causalidad.
    Sólo devuelve una dirección si existe al menos una observación explícita.
    """
    if not events:
        return RedTeamFeedbackDirection.NONE

    directions = {
        event.direction
        for event in events
        if event.measurable
    }

    if RedTeamFeedbackDirection.AMPLIFYING in directions:
        return RedTeamFeedbackDirection.AMPLIFYING

    if RedTeamFeedbackDirection.DAMPENING in directions:
        return RedTeamFeedbackDirection.DAMPENING

    return RedTeamFeedbackDirection.UNKNOWN


# -----------------------------------------------------------------------------
# 12. Pruebas de dependencia de fuente
# -----------------------------------------------------------------------------


def detect_redteam_single_source_dependence(
    *,
    baseline_supported: bool,
    evidence_ids: Sequence[str],
    independent_source_ids: Sequence[str],
    leave_one_out_results: Mapping[str, bool],
) -> tuple[bool, tuple[str, ...]]:
    """
    Test leave-one-source-out.

    Una conclusión es frágil si deja de sostenerse al retirar una única fuente
    que no tiene sustitutos independientes.
    """
    evidence = tuple(dict.fromkeys(evidence_ids))
    independent = tuple(dict.fromkeys(independent_source_ids))

    if not baseline_supported:
        return False, ()

    if len(independent) <= 1:
        return True, independent

    fragile: list[str] = []

    for source_id, result in leave_one_out_results.items():
        if source_id in independent and result is False:
            fragile.append(source_id)

    return bool(fragile), tuple(fragile)


# -----------------------------------------------------------------------------
# 13. Dependencia de umbral
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamThresholdRun:
    threshold: float
    output: float
    conclusion: str
    decision_changed: bool


def detect_redteam_threshold_dependence(
    runs: Sequence[RedTeamThresholdRun],
) -> bool:
    """
    Detecta si una conclusión cambia al modificar el umbral.

    No declara cuál umbral es correcto.
    """
    if len(runs) < 2:
        return False

    conclusions = {
        run.conclusion.strip().lower()
        for run in runs
    }

    return len(conclusions) > 1 or any(
        run.decision_changed for run in runs
    )


# -----------------------------------------------------------------------------
# 14. Dependencia de ventana temporal
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamTemporalWindowRun:
    start: str
    end: str

    output: float
    conclusion: str

    observations: int
    outcome_changed: bool


def detect_redteam_window_dependence(
    runs: Sequence[RedTeamTemporalWindowRun],
) -> bool:
    if len(runs) < 2:
        return False

    normalized = {
        run.conclusion.strip().lower()
        for run in runs
    }

    return len(normalized) > 1 or any(
        run.outcome_changed for run in runs
    )


# -----------------------------------------------------------------------------
# 15. Dependencia de denominador
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamDenominatorRun:
    denominator_name: str
    denominator_value: float
    resulting_rate: float
    conclusion: str

    def validate(self) -> None:
        if self.denominator_value <= 0:
            raise RedTeamInputError(
                "El denominador debe ser > 0"
            )

        if not isfinite(self.resulting_rate):
            raise RedTeamInputError(
                "resulting_rate debe ser finito"
            )


def detect_redteam_denominator_dependence(
    runs: Sequence[RedTeamDenominatorRun],
) -> bool:
    if len(runs) < 2:
        return False

    return len({
        run.conclusion.strip().lower()
        for run in runs
    }) > 1


# -----------------------------------------------------------------------------
# 16. Dependencia del modelo
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamModelRun:
    model_name: str
    output: float
    conclusion: str

    assumptions: tuple[str, ...] = ()
    out_of_sample: bool = False


def detect_redteam_model_dependence(
    runs: Sequence[RedTeamModelRun],
) -> bool:
    if len(runs) < 2:
        return False

    return len({
        run.conclusion.strip().lower()
        for run in runs
    }) > 1


# -----------------------------------------------------------------------------
# 17. Dependencia del prior
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamPriorRun:
    prior_name: str
    posterior: float
    conclusion: str


def detect_redteam_prior_dependence(
    runs: Sequence[RedTeamPriorRun],
) -> bool:
    if len(runs) < 2:
        return False

    return len({
        run.conclusion.strip().lower()
        for run in runs
    }) > 1


# -----------------------------------------------------------------------------
# 18. Perturbación de parámetros
# -----------------------------------------------------------------------------


def redteam_relative_change(
    baseline: float,
    perturbed: float,
) -> float | None:
    if not all(isfinite(float(value)) for value in (baseline, perturbed)):
        raise RedTeamInputError(
            "baseline y perturbed deben ser finitos"
        )

    if baseline == 0.0:
        return None

    return abs(perturbed - baseline) / abs(baseline)


def redteam_perturbation_effect(
    *,
    baseline: float,
    perturbed: float,
    tolerance: float,
) -> bool:
    """
    Devuelve True si la diferencia excede la tolerancia explícita.

    Nunca establece la tolerancia por defecto.
    """
    if tolerance < 0:
        raise RedTeamInputError(
            "tolerance no puede ser negativa"
        )

    return abs(perturbed - baseline) > tolerance


# -----------------------------------------------------------------------------
# 19. Evaluación de reproducibilidad
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamReproducibilityRun:
    run_id: str
    target_id: str
    environment: str

    software_version: str
    data_version: str
    result: float

    reproduced: bool
    absolute_difference: float

    tolerance: float

    notes: str = ""

    def validate(self) -> None:
        if self.absolute_difference < 0:
            raise RedTeamInputError(
                "absolute_difference no puede ser negativa"
            )

        if self.tolerance < 0:
            raise RedTeamInputError(
                "tolerance no puede ser negativa"
            )


def assess_redteam_reproducibility(
    runs: Sequence[RedTeamReproducibilityRun],
) -> float | None:
    if not runs:
        return None

    for run in runs:
        run.validate()

    return sum(
        1.0
        for run in runs
        if run.reproduced
        and run.absolute_difference <= run.tolerance
    ) / len(runs)


# -----------------------------------------------------------------------------
# 20. Stress testing de eventos raros
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamRareEventRun:
    base_rate: float
    positive_predictions: int
    true_positives: int
    false_positives: int
    false_negatives: int

    decision_threshold: float | None = None

    def validate(self) -> None:
        if not 0.0 <= self.base_rate <= 1.0:
            raise RedTeamInputError(
                "base_rate debe estar entre 0 y 1"
            )

        counts = (
            self.positive_predictions,
            self.true_positives,
            self.false_positives,
            self.false_negatives,
        )

        if any(count < 0 for count in counts):
            raise RedTeamInputError(
                "Los recuentos de eventos no pueden ser negativos"
            )

        if self.decision_threshold is not None:
            if not 0.0 <= self.decision_threshold <= 1.0:
                raise RedTeamInputError(
                    "decision_threshold debe estar entre 0 y 1"
                )


def redteam_positive_predictive_value(
    true_positives: int,
    false_positives: int,
) -> float | None:
    denominator = true_positives + false_positives

    if denominator == 0:
        return None

    return true_positives / denominator


# -----------------------------------------------------------------------------
# 21. Costes asimétricos FP/FN
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamDecisionCost:
    false_positive_cost: float
    false_negative_cost: float

    def validate(self) -> None:
        if self.false_positive_cost < 0:
            raise RedTeamInputError(
                "false_positive_cost no puede ser negativa"
            )

        if self.false_negative_cost < 0:
            raise RedTeamInputError(
                "false_negative_cost no puede ser negativa"
            )


def redteam_expected_error_cost(
    *,
    false_positives: int,
    false_negatives: int,
    cost: RedTeamDecisionCost,
) -> float:
    cost.validate()

    if false_positives < 0 or false_negatives < 0:
        raise RedTeamInputError(
            "Los recuentos de error no pueden ser negativos"
        )

    return (
        false_positives * cost.false_positive_cost
        + false_negatives * cost.false_negative_cost
    )


# -----------------------------------------------------------------------------
# 22. Ataques de integridad de información
# -----------------------------------------------------------------------------


class RedTeamIntegrityStatus(str, Enum):
    CLEAN = "clean"
    SUSPECT = "suspect"
    COMPROMISED = "compromised"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RedTeamInformationIntegrityCheck:
    object_id: str

    provenance_present: bool
    timestamp_valid: bool
    source_lineage_known: bool
    duplicate_checked: bool
    synthetic_content_checked: bool
    instruction_content_checked: bool

    status: RedTeamIntegrityStatus
    findings: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.object_id.strip():
            raise RedTeamInputError(
                "object_id no puede estar vacío"
            )

        if self.status == RedTeamIntegrityStatus.CLEAN:
            required = (
                self.provenance_present,
                self.timestamp_valid,
                self.source_lineage_known,
                self.duplicate_checked,
                self.synthetic_content_checked,
                self.instruction_content_checked,
            )

            if not all(required):
                raise RedTeamInputError(
                    "No puede declararse CLEAN sin haber completado los "
                    "controles de integridad"
                )


# -----------------------------------------------------------------------------
# 23. Ataques contra IA generativa
# -----------------------------------------------------------------------------


class RedTeamAIThreat(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    INDIRECT_PROMPT_INJECTION = "indirect_prompt_injection"
    DATA_POISONING = "data_poisoning"
    FABRICATED_CITATION = "fabricated_citation"
    FABRICATED_EVIDENCE = "fabricated_evidence"
    INSTRUCTION_HIJACKING = "instruction_hijacking"
    AUTOMATION_BIAS = "automation_bias"
    MODEL_EXTRACTION = "model_extraction"
    MEMBERSHIP_INFERENCE = "membership_inference"
    MODEL_INVERSION = "model_inversion"
    OUTPUT_ORACLE = "output_oracle"
    SELF_CONFIRMATION = "self_confirmation"


@dataclass(frozen=True)
class RedTeamAIAdversarialTest:
    test_id: str
    target_id: str
    threat: RedTeamAIThreat

    attack_description: str
    observed_behavior: str

    attack_successful: bool
    severity: RedTeamSeverity

    mitigation: str | None = None
    residual_risk: str | None = None

    def validate(self) -> None:
        if not self.attack_description.strip():
            raise RedTeamInputError(
                "Debe describirse el ataque"
            )

        if not self.observed_behavior.strip():
            raise RedTeamInputError(
                "Debe registrarse el comportamiento observado"
            )

        if self.attack_successful and not self.mitigation:
            raise RedTeamInputError(
                "Un ataque exitoso debe tener mitigación registrada"
            )


# -----------------------------------------------------------------------------
# 24. Evaluación de escenarios extremos
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamExtremeScenario:
    scenario_id: str
    target_id: str

    description: str

    perturbations: Mapping[str, float]
    expected_effect: str
    observed_effect: str

    remained_operational: bool
    crossed_threshold: bool

    uncertainty: str

    def validate(self) -> None:
        if not self.description.strip():
            raise RedTeamInputError(
                "El escenario necesita descripción"
            )

        if not self.uncertainty.strip():
            raise RedTeamInputError(
                "El escenario debe conservar incertidumbre explícita"
            )


# -----------------------------------------------------------------------------
# 25. Contrafactuales
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamCounterfactual:
    counterfactual_id: str
    target_id: str

    intervention: str
    observed_world: str
    counterfactual_world: str

    outcome_observed: str
    outcome_counterfactual: str

    identification_assumption: str
    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.intervention.strip():
            raise RedTeamInputError(
                "El contrafactual debe definir la intervención"
            )

        if not self.identification_assumption.strip():
            raise RedTeamInputError(
                "Un contrafactual requiere supuestos de identificación explícitos"
            )


# -----------------------------------------------------------------------------
# 26. Registro de ataques
# -----------------------------------------------------------------------------


@dataclass
class RedTeamAttackRecord:
    attack_id: str
    target_id: str

    attack_type: RedTeamAttackType
    severity: RedTeamSeverity

    description: str
    outcome: RedTeamAttackOutcome

    evidence_ids: tuple[str, ...] = ()
    critique_ids: tuple[str, ...] = ()
    test_ids: tuple[str, ...] = ()

    resolved: bool = False

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    resolution: str | None = None

    def validate(self) -> None:
        if not self.attack_id.strip():
            raise RedTeamInputError(
                "attack_id no puede estar vacío"
            )

        if not self.target_id.strip():
            raise RedTeamInputError(
                "target_id no puede estar vacío"
            )

        if not self.description.strip():
            raise RedTeamInputError(
                "El ataque debe describirse"
            )

        if self.resolved and not self.resolution:
            raise RedTeamInputError(
                "Un ataque marcado como resuelto debe tener resolución"
            )


# -----------------------------------------------------------------------------
# 27. Registro de una afirmación sometida a Red Team
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamTarget:
    target_id: str

    claim: str
    claim_type: str

    evidence_ids: tuple[str, ...]
    independent_source_ids: tuple[str, ...]

    assumptions: tuple[str, ...] = ()

    operational_use_requested: bool = False
    human_review_required: bool = True

    falsifiability: RedTeamFalsifiabilityAssessment | None = None

    def validate(self) -> None:
        if not self.claim.strip():
            raise RedTeamInputError(
                "La afirmación no puede estar vacía"
            )

        if not self.evidence_ids:
            raise RedTeamInputError(
                "Una afirmación operacional no puede carecer de trazabilidad "
                "de evidencia"
            )

        if self.operational_use_requested and not self.human_review_required:
            raise RedTeamInputError(
                "Las salidas operacionales de CeutIA requieren revisión humana"
            )


# -----------------------------------------------------------------------------
# 28. Informe completo
# -----------------------------------------------------------------------------


@dataclass
class RedTeamReport:
    target_id: str

    decision: RedTeamPromotionDecision

    attacks: list[RedTeamAttackRecord] = field(default_factory=list)
    critiques: list[RedTeamExpertCritique] = field(default_factory=list)
    tests: list[RedTeamRefutationTest] = field(default_factory=list)

    sensitivity_runs: list[RedTeamSensitivityRun] = field(
        default_factory=list
    )

    competing_hypotheses: list[RedTeamCompetingHypothesis] = field(
        default_factory=list
    )

    epistemic_debt: list[RedTeamEpistemicDebtItem] = field(
        default_factory=list
    )

    robustness: RedTeamRobustnessAssessment | None = None

    minimum_evidence: RedTeamMinimumEvidenceAnalysis | None = None

    feedback_direction: RedTeamFeedbackDirection = (
        RedTeamFeedbackDirection.NONE
    )

    critical_findings: list[str] = field(default_factory=list)
    major_findings: list[str] = field(default_factory=list)
    reservations: list[str] = field(default_factory=list)

    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# -----------------------------------------------------------------------------
# 29. Cálculo de robustez
# -----------------------------------------------------------------------------


def build_redteam_robustness_assessment(
    target_id: str,
    attacks: Sequence[RedTeamAttackRecord],
) -> RedTeamRobustnessAssessment:
    assessment = RedTeamRobustnessAssessment(target_id=target_id)

    assessment.attack_count = len(attacks)
    assessment.refuted_count = sum(
        attack.outcome == RedTeamAttackOutcome.REFUTED
        for attack in attacks
    )
    assessment.weakened_count = sum(
        attack.outcome == RedTeamAttackOutcome.WEAKENED
        for attack in attacks
    )
    assessment.survived_count = sum(
        attack.outcome == RedTeamAttackOutcome.SURVIVED
        for attack in attacks
    )
    assessment.inconclusive_count = sum(
        attack.outcome == RedTeamAttackOutcome.INCONCLUSIVE
        for attack in attacks
    )

    assessment.unresolved_major_attacks = sum(
        attack.severity == RedTeamSeverity.MAJOR
        and not attack.resolved
        for attack in attacks
    )

    assessment.unresolved_critical_attacks = sum(
        attack.severity == RedTeamSeverity.CRITICAL
        and not attack.resolved
        for attack in attacks
    )

    return assessment


# -----------------------------------------------------------------------------
# 30. Evaluación de fragilidad
# -----------------------------------------------------------------------------


def redteam_fragility_flags(
    *,
    source_dependence: bool,
    threshold_dependence: bool,
    window_dependence: bool,
    denominator_dependence: bool,
    model_dependence: bool,
    prior_dependence: bool,
    feedback_detected: bool,
) -> tuple[str, ...]:
    flags: list[str] = []

    if source_dependence:
        flags.append("single_or_dependent_source")

    if threshold_dependence:
        flags.append("threshold_dependence")

    if window_dependence:
        flags.append("temporal_window_dependence")

    if denominator_dependence:
        flags.append("denominator_dependence")

    if model_dependence:
        flags.append("model_dependence")

    if prior_dependence:
        flags.append("prior_dependence")

    if feedback_detected:
        flags.append("ceutia_feedback")

    return tuple(flags)


# -----------------------------------------------------------------------------
# 31. Construcción de deuda epistémica
# -----------------------------------------------------------------------------


def build_redteam_epistemic_debt(
    *,
    target_id: str,
    unresolved_attacks: Sequence[RedTeamAttackRecord],
    competing_hypotheses: Sequence[RedTeamCompetingHypothesis],
) -> list[RedTeamEpistemicDebtItem]:
    debt: list[RedTeamEpistemicDebtItem] = []

    for index, attack in enumerate(unresolved_attacks, start=1):
        debt.append(
            RedTeamEpistemicDebtItem(
                debt_id=f"{target_id}:debt:{index}",
                target_id=target_id,
                statement=(
                    f"Ataque no resuelto sobre '{target_id}': "
                    f"{attack.attack_type.value}"
                ),
                missing_information=attack.description,
                reason_missing=(
                    "La prueba disponible no permite cerrar el ataque "
                    "epistemológico de forma concluyente."
                ),
                resolving_data=attack.evidence_ids,
                competing_hypotheses=tuple(
                    hypothesis.hypothesis_id
                    for hypothesis in competing_hypotheses
                ),
                discriminating_observation=None,
                responsible_party=None,
                priority=(
                    1
                    if attack.severity == RedTeamSeverity.CRITICAL
                    else 2
                ),
            )
        )

    return debt


# -----------------------------------------------------------------------------
# 32. Criterios de promoción
# -----------------------------------------------------------------------------


def evaluate_redteam_promotion(
    *,
    attacks: Sequence[RedTeamAttackRecord],
    falsifiable: bool,
    operational_use_requested: bool,
    robustness: RedTeamRobustnessAssessment | None,
    single_source_failure: bool,
    feedback_detected: bool,
) -> RedTeamPromotionDecision:
    """
    Motor conservador de promoción.

    No utiliza una puntuación mágica.

    La decisión se basa en condiciones explícitas y auditables.
    """

    critical_unresolved = any(
        attack.severity == RedTeamSeverity.CRITICAL
        and not attack.resolved
        for attack in attacks
    )

    major_unresolved = any(
        attack.severity == RedTeamSeverity.MAJOR
        and not attack.resolved
        for attack in attacks
    )

    refuted = any(
        attack.outcome == RedTeamAttackOutcome.REFUTED
        for attack in attacks
    )

    if refuted:
        return RedTeamPromotionDecision.BLOCK

    if critical_unresolved:
        return RedTeamPromotionDecision.BLOCK

    if operational_use_requested and not falsifiable:
        return RedTeamPromotionDecision.BLOCK

    if single_source_failure:
        return RedTeamPromotionDecision.SHADOW_ONLY

    if feedback_detected:
        return RedTeamPromotionDecision.SHADOW_ONLY

    if major_unresolved:
        return RedTeamPromotionDecision.SHADOW_ONLY

    if robustness is not None:
        if robustness.unresolved_critical_attacks > 0:
            return RedTeamPromotionDecision.BLOCK

        if robustness.unresolved_major_attacks > 0:
            return RedTeamPromotionDecision.SHADOW_ONLY

    if operational_use_requested:
        return RedTeamPromotionDecision.PASS_WITH_RESERVATIONS

    return RedTeamPromotionDecision.PASS


# -----------------------------------------------------------------------------
# 33. Orquestador principal
# -----------------------------------------------------------------------------


def run_scientific_red_team(
    *,
    target: RedTeamTarget,
    attacks: Sequence[RedTeamAttackRecord] = (),
    critiques: Sequence[RedTeamExpertCritique] = (),
    tests: Sequence[RedTeamRefutationTest] = (),
    sensitivity_runs: Sequence[RedTeamSensitivityRun] = (),
    competing_hypotheses: Sequence[RedTeamCompetingHypothesis] = (),
    feedback_events: Sequence[RedTeamFeedbackEvent] = (),
    falsifiability: RedTeamFalsifiabilityAssessment | None = None,
    minimum_evidence: RedTeamMinimumEvidenceAnalysis | None = None,
) -> RedTeamReport:
    """
    Ejecuta la capa Scientific Red Team sobre una afirmación.

    Esta función NO recalcula modelos científicos. Orquesta las pruebas y
    conserva sus resultados epistemológicos.
    """

    target.validate()

    for critique in critiques:
        critique.validate()

    for test in tests:
        test.validate()

    for attack in attacks:
        attack.validate()

    for run in sensitivity_runs:
        run.validate()

    for hypothesis in competing_hypotheses:
        hypothesis.validate()

    for event in feedback_events:
        event.validate()

    if falsifiability is not None:
        falsifiability.validate()

    if minimum_evidence is not None:
        minimum_evidence.validate()

    robustness = build_redteam_robustness_assessment(
        target.target_id,
        attacks,
    )

    feedback_direction = detect_redteam_feedback_loop(
        feedback_events
    )

    single_source_failure = (
        minimum_evidence.single_source_failure
        if minimum_evidence is not None
        else False
    )

    decision = evaluate_redteam_promotion(
        attacks=attacks,
        falsifiable=(
            falsifiability.falsifiable
            if falsifiability is not None
            else False
        ),
        operational_use_requested=target.operational_use_requested,
        robustness=robustness,
        single_source_failure=single_source_failure,
        feedback_detected=(
            feedback_direction
            == RedTeamFeedbackDirection.AMPLIFYING
        ),
    )

    report = RedTeamReport(
        target_id=target.target_id,
        decision=decision,
        attacks=list(attacks),
        critiques=list(critiques),
        tests=list(tests),
        sensitivity_runs=list(sensitivity_runs),
        competing_hypotheses=list(competing_hypotheses),
        robustness=robustness,
        minimum_evidence=minimum_evidence,
        feedback_direction=feedback_direction,
    )

    unresolved = [
        attack
        for attack in attacks
        if not attack.resolved
    ]

    report.epistemic_debt.extend(
        build_redteam_epistemic_debt(
            target_id=target.target_id,
            unresolved_attacks=unresolved,
            competing_hypotheses=competing_hypotheses,
        )
    )

    for attack in attacks:
        if attack.severity == RedTeamSeverity.CRITICAL:
            report.critical_findings.append(
                f"{attack.attack_type.value}: {attack.description}"
            )
        elif attack.severity == RedTeamSeverity.MAJOR:
            report.major_findings.append(
                f"{attack.attack_type.value}: {attack.description}"
            )

    if single_source_failure:
        report.reservations.append(
            "La conclusión depende de una fuente o linaje no sustituible "
            "por evidencia independiente."
        )

    if feedback_direction == RedTeamFeedbackDirection.AMPLIFYING:
        report.reservations.append(
            "Se ha observado posible feedback amplificador asociado a "
            "salidas de CeutIA; la interpretación causal permanece abierta."
        )

    if falsifiability is None:
        report.reservations.append(
            "No se ha registrado evaluación explícita de falsabilidad."
        )

    return report


# -----------------------------------------------------------------------------
# 34. Elegibilidad operacional
# -----------------------------------------------------------------------------


def assert_redteam_operational_eligibility(
    report: RedTeamReport,
) -> None:
    """
    Impide que un resultado bloqueado o sólo apto para shadow mode se trate
    como salida operacional.
    """

    if report.decision in {
        RedTeamPromotionDecision.BLOCK,
        RedTeamPromotionDecision.SHADOW_ONLY,
    }:
        raise RedTeamCriticalFinding(
            f"El target '{report.target_id}' no es elegible para uso "
            f"operacional: {report.decision.value}"
        )


# -----------------------------------------------------------------------------
# 35. Resumen auditable
# -----------------------------------------------------------------------------


def summarize_scientific_red_team(
    report: RedTeamReport,
) -> dict[str, Any]:
    """
    Serialización simple para logging, auditoría o API.

    No expone automáticamente evidencia sensible.
    """

    return {
        "target_id": report.target_id,
        "decision": report.decision.value,
        "attack_count": len(report.attacks),
        "critique_count": len(report.critiques),
        "test_count": len(report.tests),
        "sensitivity_run_count": len(report.sensitivity_runs),
        "competing_hypothesis_count": len(report.competing_hypotheses),
        "epistemic_debt_count": len(report.epistemic_debt),
        "critical_findings": len(report.critical_findings),
        "major_findings": len(report.major_findings),
        "feedback_direction": report.feedback_direction.value,
        "robustness": (
            None
            if report.robustness is None
            else {
                "minimum": report.robustness.minimum_score,
                "mean": report.robustness.mean_score,
                "attacks": report.robustness.attack_count,
                "refuted": report.robustness.refuted_count,
                "weakened": report.robustness.weakened_count,
                "survived": report.robustness.survived_count,
                "inconclusive": report.robustness.inconclusive_count,
            }
        ),
        "generated_at": report.generated_at.isoformat(),
    }


# -----------------------------------------------------------------------------
# 36. Consistencia de pruebas
# -----------------------------------------------------------------------------


def validate_redteam_test_consistency(
    *,
    critiques: Sequence[RedTeamExpertCritique],
    tests: Sequence[RedTeamRefutationTest],
) -> tuple[str, ...]:
    """
    Detecta pruebas huérfanas o críticas sin prueba asociada.

    No exige que toda crítica pueda resolverse automáticamente.
    """

    critique_ids = {
        critique.critique_id
        for critique in critiques
    }

    findings: list[str] = []

    for test in tests:
        if test.critique_id not in critique_ids:
            findings.append(
                f"Prueba '{test.test_id}' referencia una crítica inexistente."
            )

    tested_critique_ids = {
        test.critique_id
        for test in tests
    }

    for critique in critiques:
        if (
            critique.required_test.strip()
            and critique.critique_id not in tested_critique_ids
        ):
            findings.append(
                f"Crítica '{critique.critique_id}' todavía no tiene "
                "prueba registrada."
            )

    return tuple(findings)


# -----------------------------------------------------------------------------
# 37. Consistencia epistemológica
# -----------------------------------------------------------------------------


def validate_redteam_epistemic_consistency(
    report: RedTeamReport,
) -> tuple[str, ...]:
    """
    Comprueba invariantes de interpretación.

    Especialmente evita:
        survived -> true
        robust -> causal
        corroborated -> independent
    """

    findings: list[str] = []

    for attack in report.attacks:
        if attack.outcome == RedTeamAttackOutcome.SURVIVED:
            # Se conserva como comprobación documental, no como error.
            if attack.resolution:
                normalized = attack.resolution.lower()
                if any(
                    token in normalized
                    for token in (
                        "verdadero",
                        "truth",
                        "proven",
                        "demostrado",
                    )
                ):
                    findings.append(
                        f"El ataque '{attack.attack_id}' interpreta "
                        "SURVIVED como demostración de verdad."
                    )

    if report.robustness is not None:
        if (
            report.robustness.minimum_score is not None
            and report.robustness.minimum_score > 1.0
        ):
            findings.append(
                "Score de robustez fuera de rango."
            )

    return tuple(findings)


# -----------------------------------------------------------------------------
# 38. Registro de principios científicos
# -----------------------------------------------------------------------------


SCIENTIFIC_RED_TEAM_INVARIANTS: Final[tuple[str, ...]] = (
    "Una conclusión que sobrevive un ataque no se convierte por ello en verdad.",
    "Robustez no equivale a validez.",
    "Validez no equivale a causalidad.",
    "Causalidad no equivale a utilidad operacional.",
    "Corroboración no equivale a independencia.",
    "Número de fuentes no equivale a cantidad de evidencia independiente.",
    "Una fuente única puede sostener una observación, pero no debe aparentar corroboración.",
    "Toda afirmación operacional importante debe disponer de una vía explícita de falsación.",
    "Una hipótesis que puede explicar cualquier resultado no es falsable.",
    "Una hipótesis no debe modificarse retrospectivamente sólo para evitar refutación.",
    "Los resultados inconclusos deben conservarse como inconclusos.",
    "La ausencia de evidencia no equivale automáticamente a evidencia de ausencia.",
    "Cambiar el denominador puede cambiar la interpretación de una tasa.",
    "Cambiar la ventana temporal puede cambiar la interpretación de una tendencia.",
    "Cambiar la unidad espacial puede cambiar la asociación observada.",
    "Cambiar el modelo puede cambiar la conclusión.",
    "Cambiar el prior puede cambiar el posterior.",
    "Cambiar el umbral puede cambiar una decisión.",
    "Los parámetros no deben recibir tolerancias arbitrarias sin justificación.",
    "La sensibilidad no debe confundirse con especificidad.",
    "La discriminación no demuestra calibración.",
    "La calibración no demuestra causalidad.",
    "El rendimiento fuera de muestra es distinto del ajuste interno.",
    "La reproducibilidad debe conservar versión de datos y software.",
    "El feedback generado por CeutIA puede contaminar la observación posterior.",
    "Una intervención modifica el sistema que CeutIA intenta observar.",
    "CeutIA no debe utilizar su propia salida como confirmación independiente.",
    "Una alerta que provoca conducta puede alterar la tasa futura del evento observado.",
    "La información debe conservar procedencia y linaje.",
    "El contenido sintético no debe convertirse silenciosamente en evidencia.",
    "El contenido adversarial no debe eliminarse del análisis sólo por ser incómodo.",
    "El contenido adversarial debe separarse de su valor probatorio.",
    "La crítica experta es un ataque epistemológico, no evidencia primaria.",
    "El red team debe poder producir resultados negativos.",
    "No debe existir una ruta de promoción que dependa únicamente de supervivencia a ataques.",
    "Una conclusión frágil debe poder degradarse a shadow mode.",
    "Una refutación crítica debe bloquear la promoción operacional.",
    "La deuda epistémica debe permanecer visible hasta su resolución o aceptación explícita.",
    "Toda incertidumbre material debe conservarse en la salida interna.",
    "La ausencia de falsación no autoriza lenguaje de certeza.",
    "La confianza de CeutIA debe actualizarse por evidencia, no por repetición interna.",
)


# -----------------------------------------------------------------------------
# 39. Validación estática de invariantes
# -----------------------------------------------------------------------------


def validate_scientific_red_team_invariants() -> tuple[str, ...]:
    """
    Devuelve los invariantes declarados.

    Esta función permite que tests o CI verifiquen que la capa conserva
    explícitamente sus principios epistemológicos.
    """

    if len(SCIENTIFIC_RED_TEAM_INVARIANTS) < 30:
        raise RedTeamError(
            "El registro de invariantes Scientific Red Team es "
            "sospechosamente incompleto."
        )

    return SCIENTIFIC_RED_TEAM_INVARIANTS


# -----------------------------------------------------------------------------
# 40. Función de comparación de conclusiones
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamConclusionComparison:
    baseline: str
    alternative: str

    changed: bool
    materially_weakened: bool

    explanation: str


def compare_redteam_conclusions(
    *,
    baseline: str,
    alternative: str,
) -> RedTeamConclusionComparison:
    """
    Comparación textual conservadora.

    No intenta interpretar semánticamente una conclusión científica.
    La interpretación sustantiva debe proceder del evaluador/modelo
    correspondiente.
    """

    baseline_normalized = " ".join(
        baseline.lower().split()
    )

    alternative_normalized = " ".join(
        alternative.lower().split()
    )

    changed = baseline_normalized != alternative_normalized

    return RedTeamConclusionComparison(
        baseline=baseline,
        alternative=alternative,
        changed=changed,
        materially_weakened=changed,
        explanation=(
            "La conclusión textual cambió; debe realizarse una evaluación "
            "sustantiva para determinar si el cambio es material."
        ),
    )


# -----------------------------------------------------------------------------
# 41. Evaluación de independencia epistemológica
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RedTeamSourceRelation:
    source_id: str
    parent_source_id: str | None
    common_origin_id: str | None

    dependency: RedTeamEvidenceDependency


def count_redteam_effective_independent_sources(
    relations: Sequence[RedTeamSourceRelation],
) -> int:
    """
    Cuenta fuentes independientes de forma conservadora.

    Si varias fuentes comparten origen conocido, no se cuentan como
    corroboración independiente.
    """

    if not relations:
        return 0

    independent_groups: set[str] = set()

    for relation in relations:
        if relation.dependency == RedTeamEvidenceDependency.DEPENDENT:
            continue

        group = (
            relation.common_origin_id
            or relation.parent_source_id
            or relation.source_id
        )

        independent_groups.add(group)

    return len(independent_groups)


# -----------------------------------------------------------------------------
# 42. Auditoría de lenguaje epistemológico
# -----------------------------------------------------------------------------


_REDTEAM_OVERCLAIM_TERMS: Final[tuple[str, ...]] = (
    "demuestra",
    "demostrado",
    "sin duda",
    "certeza",
    "inequívoco",
    "inequívocamente",
    "predice con certeza",
    "causa",
)


def redteam_detect_overclaim_language(
    text: str,
) -> tuple[str, ...]:
    """
    Detector deliberadamente simple de sobreafirmación.

    No determina si una frase es científicamente correcta.
    Sólo identifica lenguaje que requiere revisión epistemológica.
    """

    normalized = " ".join(text.lower().split())

    return tuple(
        term
        for term in _REDTEAM_OVERCLAIM_TERMS
        if term in normalized
    )


# -----------------------------------------------------------------------------
# 43. Prohibición de equivalencias epistemológicas inválidas
# -----------------------------------------------------------------------------


def assert_redteam_no_epistemic_equivalence(
    *,
    robustness: bool = False,
    validity: bool = False,
    causal: bool = False,
    operational_utility: bool = False,
) -> None:
    """
    Impide que una propiedad se interprete automáticamente como otra.

    Se mantiene como función explícita porque estos errores son frecuentes
    precisamente en sistemas de inteligencia automatizada.
    """

    if robustness and not validity:
        # Permitido: robustez puede existir sin validez.
        return

    if causal and not validity:
        raise RedTeamError(
            "No puede declararse causalidad sin una base de validez explícita."
        )

    if operational_utility and not validity:
        raise RedTeamError(
            "No puede declararse utilidad operacional sobre un resultado "
            "sin validez establecida."
        )


# -----------------------------------------------------------------------------
# 44. Exportación controlada de símbolos
# -----------------------------------------------------------------------------
#
# No reemplaza el __all__ existente si ya existe. Se mantiene un conjunto
# adicional para permitir integración progresiva.
# -----------------------------------------------------------------------------


SCIENTIFIC_RED_TEAM_EXPORTS: Final[tuple[str, ...]] = (
    "RedTeamAttackType",
    "RedTeamAttackOutcome",
    "RedTeamSeverity",
    "RedTeamRobustnessDimension",
    "RedTeamEvidenceDependency",
    "RedTeamDebtStatus",
    "RedTeamPromotionDecision",
    "RedTeamExpertCritique",
    "RedTeamRefutationTest",
    "RedTeamSensitivityRun",
    "RedTeamRobustnessAssessment",
    "RedTeamEvidenceSet",
    "RedTeamMinimumEvidenceAnalysis",
    "RedTeamCompetingHypothesis",
    "RedTeamFalsifiabilityAssessment",
    "RedTeamEpistemicDebtItem",
    "RedTeamFeedbackEvent",
    "RedTeamAttackRecord",
    "RedTeamTarget",
    "RedTeamReport",
    "RedTeamInformationIntegrityCheck",
    "RedTeamAIThreat",
    "RedTeamAIAdversarialTest",
    "RedTeamExtremeScenario",
    "RedTeamCounterfactual",
    "RedTeamReproducibilityRun",
    "RedTeamDecisionCost",
    "run_scientific_red_team",
    "assert_redteam_operational_eligibility",
    "summarize_scientific_red_team",
    "validate_scientific_red_team_invariants",
)


# =============================================================================
# FIN — SCIENTIFIC RED TEAM / FALSIFICATION ENGINE
# =============================================================================# ============================================================================
# CEUTIA — ADVANCED ADVERSARIAL VALIDATION EXTENSION
# ============================================================================
#
# This extension adds machine-checkable safeguards for:
#
#   1. Data integrity and poisoning
#   2. Temporal leakage and look-ahead bias
#   3. Causal validity
#   4. Rare-event prediction
#   5. Complex-systems dynamics
#   6. Capacity / queueing validation
#   7. Spatial and spatiotemporal validity
#   8. Information propagation and source dependency
#   9. CeutIA-generated feedback loops
#  10. Scenario and hypothesis integrity
#  11. Adversarial AI / LLM security
#  12. Self-impact and intervention evaluation
#  13. Epistemic firewalling
#
# DESIGN PRINCIPLE:
#
# No conclusion produced by CeutIA may increase its own evidential weight.
#
# A prediction is not evidence for itself.
# An alert is not independent corroboration.
# A model-generated hypothesis is not an observation.
# A public intervention can modify the system being monitored and must
# therefore be recorded as an intervention/feedback event.
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from math import isfinite, log
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# EXTENDED ENUMERATIONS
# ============================================================================


class AdvancedFindingCode(str, Enum):
    """Machine-readable failure modes for advanced validation."""

    DATA_POISONING = "data_poisoning"
    DATA_DUPLICATION = "data_duplication"
    DATA_SYNTHETIC_CONTAMINATION = "data_synthetic_contamination"
    DATA_DEFINITION_CHANGE = "data_definition_change"
    DATA_UNIT_ERROR = "data_unit_error"
    DATA_TIMESTAMP_ERROR = "data_timestamp_error"
    DATA_BACKFILL = "data_backfill"
    DATA_CENSORING = "data_censoring"
    DATA_MISSINGNESS_MECHANISM_UNKNOWN = "data_missingness_mechanism_unknown"

    TEMPORAL_LEAKAGE = "temporal_leakage"
    LOOK_AHEAD_BIAS = "look_ahead_bias"
    POST_OUTCOME_INFORMATION = "post_outcome_information"
    INVALID_TEMPORAL_SPLIT = "invalid_temporal_split"
    REGIME_CHANGE = "regime_change"

    CONFOUNDING = "confounding"
    COLLIDER_BIAS = "collider_bias"
    SELECTION_BIAS = "selection_bias"
    IMMORTAL_TIME_BIAS = "immortal_time_bias"
    REVERSE_CAUSALITY = "reverse_causality"
    ECOLOGICAL_FALLACY = "ecological_fallacy"
    SIMPSON_PARADOX = "simpson_paradox"
    UNMEASURED_CONFOUNDING = "unmeasured_confounding"
    CAUSAL_IDENTIFICATION_MISSING = "causal_identification_missing"

    RARE_EVENT_BIAS = "rare_event_bias"
    CLASS_IMBALANCE = "class_imbalance"
    BASE_RATE_NEGLECT = "base_rate_neglect"
    OVERDISPERSION = "overdispersion"
    ZERO_INFLATION = "zero_inflation"
    EVENT_DEFINITION_MISSING = "event_definition_missing"

    COMPLEX_DYNAMICS_UNASSESSED = "complex_dynamics_unassessed"
    FEEDBACK_UNASSESSED = "feedback_unassessed"
    HYSTERESIS_UNASSESSED = "hysteresis_unassessed"
    REGIME_TRANSITION_UNASSESSED = "regime_transition_unassessed"
    CASCADE_RISK_UNASSESSED = "cascade_risk_unassessed"
    CRITICAL_TRANSITION_UNASSESSED = "critical_transition_unassessed"
    RESILIENCE_UNASSESSED = "resilience_unassessed"

    CAPACITY_DEFINITION_MISSING = "capacity_definition_missing"
    BOTTLENECK_UNASSESSED = "bottleneck_unassessed"
    QUEUEING_MODEL_MISSING = "queueing_model_missing"
    TRANSIENT_SURGE_UNASSESSED = "transient_surge_unassessed"
    RECOVERY_CAPACITY_UNASSESSED = "recovery_capacity_unassessed"

    SPATIAL_AUTOCORRELATION = "spatial_autocorrelation"
    SPATIAL_DEPENDENCE = "spatial_dependence"
    MAUP_RISK = "maup_risk"
    SPATIAL_DENOMINATOR_ERROR = "spatial_denominator_error"
    SPATIOTEMPORAL_CLUSTER_UNASSESSED = "spatiotemporal_cluster_unassessed"

    SOURCE_LINEAGE_UNKNOWN = "source_lineage_unknown"
    SOURCE_COMMON_ORIGIN = "source_common_origin"
    SOURCE_LAUNDERING = "source_laundering"
    CORROBORATION_NOT_INDEPENDENT = "corroboration_not_independent"

    CEUTIA_FEEDBACK = "ceutia_feedback"
    SELF_CONFIRMATION = "self_confirmation"
    INTERVENTION_CONTAMINATION = "intervention_contamination"
    BEHAVIOURAL_RESPONSE_TO_ALERT = "behavioural_response_to_alert"

    SCENARIO_ASSUMPTION_MISSING = "scenario_assumption_missing"
    SCENARIO_NOT_FALSIFIABLE = "scenario_not_falsifiable"
    COMPETING_HYPOTHESES_MISSING = "competing_hypotheses_missing"
    COUNTERFACTUAL_UNDEFINED = "counterfactual_undefined"

    PROMPT_INJECTION = "prompt_injection"
    INDIRECT_PROMPT_INJECTION = "indirect_prompt_injection"
    DATA_POISONING_AI = "data_poisoning_ai"
    MODEL_EXTRACTION = "model_extraction"
    MEMBERSHIP_INFERENCE = "membership_inference"
    MODEL_INVERSION = "model_inversion"
    OUTPUT_ORACLE = "output_oracle"
    FABRICATED_EVIDENCE = "fabricated_evidence"
    AUTOMATION_BIAS = "automation_bias"
    INSTRUCTION_HIJACKING = "instruction_hijacking"

    INTERVENTION_NOT_REGISTERED = "intervention_not_registered"
    OUTCOME_NOT_REGISTERED = "outcome_not_registered"
    IMPACT_NOT_ASSESSED = "impact_not_assessed"

    EPISTEMIC_SELF_CONFIRMATION = "epistemic_self_confirmation"


class AdvancedValidationSeverity(str, Enum):
    """Severity used by the advanced validation layer."""

    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class MissingnessMechanism(str, Enum):
    """Statistical missingness mechanisms."""

    MCAR = "MCAR"
    MAR = "MAR"
    MNAR = "MNAR"
    UNKNOWN = "UNKNOWN"


class PredictionTargetType(str, Enum):
    """Permitted prediction targets."""

    EVENT = "event"
    COUNT = "count"
    RATE = "rate"
    STATE = "state"
    TRAJECTORY = "trajectory"
    TIME_TO_EVENT = "time_to_event"
    SCENARIO = "scenario"


class FeedbackSource(str, Enum):
    """Origin of a system-level feedback effect."""

    EXTERNAL = "external"
    CEUTIA_PUBLIC_OUTPUT = "ceutia_public_output"
    CEUTIA_ALERT = "ceutia_alert"
    CEUTIA_RECOMMENDATION = "ceutia_recommendation"
    HUMAN_DECISION_AFTER_CEUTIA = "human_decision_after_ceutia"
    UNKNOWN = "unknown"


# ============================================================================
# ADVANCED FINDINGS
# ============================================================================


@dataclass(frozen=True, slots=True)
class AdvancedFinding:
    """A machine-readable finding generated by advanced validation."""

    code: AdvancedFindingCode
    severity: AdvancedValidationSeverity
    message: str
    field: str | None = None
    evidence: tuple[str, ...] = ()
    remediation: str | None = None

    @property
    def blocks_operation(self) -> bool:
        return self.severity is AdvancedValidationSeverity.CRITICAL


# ============================================================================
# DATA INTEGRITY
# ============================================================================


@dataclass(frozen=True, slots=True)
class DataIntegrityProfile:
    """
    Machine-checkable description of the integrity of a dataset.

    This class does not declare a dataset truthful. It describes whether
    integrity controls have been performed.
    """

    provenance_complete: bool
    timestamps_validated: bool
    units_validated: bool
    duplicate_check_performed: bool
    synthetic_data_check_performed: bool
    poisoning_check_performed: bool
    definition_stability_checked: bool
    backfill_detected: bool = False
    censoring_present: bool = False
    missingness_mechanism: MissingnessMechanism = MissingnessMechanism.UNKNOWN

    source_lineage_known: bool = True
    common_origin_checked: bool = False
    source_laundering_checked: bool = False

    contamination_rate: float = 0.0
    duplicate_rate: float = 0.0

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        if not self.provenance_complete:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_POISONING,
                    AdvancedValidationSeverity.MAJOR,
                    "Dataset provenance is incomplete.",
                    remediation="Require provenance before operational use.",
                )
            )

        if not self.timestamps_validated:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_TIMESTAMP_ERROR,
                    AdvancedValidationSeverity.MAJOR,
                    "Temporal semantics have not been validated.",
                    remediation="Validate event time, publication time and ingestion time.",
                )
            )

        if not self.units_validated:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_UNIT_ERROR,
                    AdvancedValidationSeverity.MAJOR,
                    "Measurement units have not been validated.",
                    remediation="Validate units and transformations against the source contract.",
                )
            )

        if not self.duplicate_check_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_DUPLICATION,
                    AdvancedValidationSeverity.MAJOR,
                    "Duplicate detection has not been performed.",
                    remediation="Run deterministic and probabilistic duplicate detection.",
                )
            )

        if not self.synthetic_data_check_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_SYNTHETIC_CONTAMINATION,
                    AdvancedValidationSeverity.MINOR,
                    "Synthetic or generated-data contamination has not been assessed.",
                )
            )

        if not self.poisoning_check_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_POISONING,
                    AdvancedValidationSeverity.MAJOR,
                    "Data poisoning checks have not been performed.",
                    remediation="Run source-integrity and anomaly/poisoning checks.",
                )
            )

        if not self.definition_stability_checked:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_DEFINITION_CHANGE,
                    AdvancedValidationSeverity.MAJOR,
                    "Source-definition stability has not been checked.",
                    remediation="Compare metadata and methodology across time.",
                )
            )

        if self.backfill_detected:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_BACKFILL,
                    AdvancedValidationSeverity.MAJOR,
                    "Backfilled observations are present.",
                    remediation="Preserve knowledge-time semantics and exclude future knowledge from historical prediction tests.",
                )
            )

        if self.censoring_present:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_CENSORING,
                    AdvancedValidationSeverity.MINOR,
                    "Censoring is present and must be represented explicitly.",
                )
            )

        if self.missingness_mechanism is MissingnessMechanism.UNKNOWN:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_MISSINGNESS_MECHANISM_UNKNOWN,
                    AdvancedValidationSeverity.MINOR,
                    "Missingness mechanism has not been characterized.",
                )
            )

        if not self.source_lineage_known:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.SOURCE_LINEAGE_UNKNOWN,
                    AdvancedValidationSeverity.MAJOR,
                    "Source lineage is unknown.",
                )
            )

        if not self.common_origin_checked:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.SOURCE_COMMON_ORIGIN,
                    AdvancedValidationSeverity.MINOR,
                    "Common-origin dependency between sources has not been checked.",
                )
            )

        if not self.source_laundering_checked:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.SOURCE_LAUNDERING,
                    AdvancedValidationSeverity.MINOR,
                    "Source laundering has not been assessed.",
                )
            )

        if not 0.0 <= self.contamination_rate <= 1.0:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_SYNTHETIC_CONTAMINATION,
                    AdvancedValidationSeverity.CRITICAL,
                    "Contamination rate is outside [0, 1].",
                )
            )

        if not 0.0 <= self.duplicate_rate <= 1.0:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.DATA_DUPLICATION,
                    AdvancedValidationSeverity.CRITICAL,
                    "Duplicate rate is outside [0, 1].",
                )
            )

        return tuple(findings)


# ============================================================================
# TEMPORAL LEAKAGE
# ============================================================================


@dataclass(frozen=True, slots=True)
class TemporalValidationProfile:
    """
    Explicit temporal semantics for a prediction.

    world_time:
        when the underlying event occurred.

    knowledge_time:
        when CeutIA could legitimately know the information.

    prediction_time:
        when the prediction was generated.

    outcome_time:
        when the target outcome became observable.
    """

    prediction_time: datetime
    outcome_time: datetime
    feature_max_knowledge_time: datetime

    temporal_split_validated: bool
    rolling_origin_validated: bool
    look_ahead_check_performed: bool
    post_outcome_check_performed: bool
    backtest_reproducible: bool

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        if self.outcome_time <= self.prediction_time:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INVALID_TEMPORAL_SPLIT,
                    AdvancedValidationSeverity.CRITICAL,
                    "Outcome time must occur after prediction time.",
                )
            )

        if self.feature_max_knowledge_time > self.prediction_time:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.TEMPORAL_LEAKAGE,
                    AdvancedValidationSeverity.CRITICAL,
                    "At least one feature was known after prediction time.",
                    remediation="Remove post-prediction information.",
                )
            )

        if not self.temporal_split_validated:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INVALID_TEMPORAL_SPLIT,
                    AdvancedValidationSeverity.MAJOR,
                    "Temporal train/validation/test separation is not validated.",
                )
            )

        if not self.rolling_origin_validated:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INVALID_TEMPORAL_SPLIT,
                    AdvancedValidationSeverity.MAJOR,
                    "Rolling-origin or equivalent temporal validation has not been performed.",
                )
            )

        if not self.look_ahead_check_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.LOOK_AHEAD_BIAS,
                    AdvancedValidationSeverity.CRITICAL,
                    "Look-ahead bias has not been explicitly checked.",
                )
            )

        if not self.post_outcome_check_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.POST_OUTCOME_INFORMATION,
                    AdvancedValidationSeverity.CRITICAL,
                    "Post-outcome information leakage has not been checked.",
                )
            )

        if not self.backtest_reproducible:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INVALID_TEMPORAL_SPLIT,
                    AdvancedValidationSeverity.MAJOR,
                    "Historical backtest cannot currently be reproduced.",
                )
            )

        return tuple(findings)


# ============================================================================
# CAUSAL VALIDITY
# ============================================================================


@dataclass(frozen=True, slots=True)
class CausalValidityProfile:
    """
    Causal-identification safeguards.

    CeutIA must not convert observational association into causal language.
    """

    causal_claim: bool

    causal_estimand_defined: bool = False
    identification_strategy_defined: bool = False
    confounding_assessed: bool = False
    selection_bias_assessed: bool = False
    collider_bias_assessed: bool = False
    reverse_causality_assessed: bool = False
    immortal_time_bias_assessed: bool = False
    unmeasured_confounding_assessed: bool = False
    ecological_level_appropriate: bool = True
    temporal_precedence_established: bool = False

    sensitivity_analysis_performed: bool = False
    dag_or_equivalent_causal_structure_available: bool = False

    def validate(self) -> tuple[AdvancedFinding, ...]:
        if not self.causal_claim:
            return ()

        findings: list[AdvancedFinding] = []

        if not self.causal_estimand_defined:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CAUSAL_IDENTIFICATION_MISSING,
                    AdvancedValidationSeverity.CRITICAL,
                    "Causal estimand is undefined.",
                )
            )

        if not self.identification_strategy_defined:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CAUSAL_IDENTIFICATION_MISSING,
                    AdvancedValidationSeverity.CRITICAL,
                    "No causal identification strategy has been specified.",
                )
            )

        if not self.confounding_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CONFOUNDING,
                    AdvancedValidationSeverity.MAJOR,
                    "Confounding has not been assessed.",
                )
            )

        if not self.selection_bias_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.SELECTION_BIAS,
                    AdvancedValidationSeverity.MAJOR,
                    "Selection bias has not been assessed.",
                )
            )

        if not self.collider_bias_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.COLLIDER_BIAS,
                    AdvancedValidationSeverity.MAJOR,
                    "Collider bias has not been assessed.",
                )
            )

        if not self.reverse_causality_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.REVERSE_CAUSALITY,
                    AdvancedValidationSeverity.MAJOR,
                    "Reverse causality has not been assessed.",
                )
            )

        if not self.immortal_time_bias_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.IMMORTAL_TIME_BIAS,
                    AdvancedValidationSeverity.MAJOR,
                    "Immortal-time bias has not been assessed.",
                )
            )

        if not self.unmeasured_confounding_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.UNMEASURED_CONFOUNDING,
                    AdvancedValidationSeverity.MAJOR,
                    "Unmeasured confounding has not been assessed.",
                )
            )

        if not self.ecological_level_appropriate:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.ECOLOGICAL_FALLACY,
                    AdvancedValidationSeverity.CRITICAL,
                    "Inference crosses an invalid ecological level.",
                )
            )

        if not self.temporal_precedence_established:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.REVERSE_CAUSALITY,
                    AdvancedValidationSeverity.MAJOR,
                    "Temporal precedence has not been established.",
                )
            )

        if not self.sensitivity_analysis_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.UNMEASURED_CONFOUNDING,
                    AdvancedValidationSeverity.MINOR,
                    "Sensitivity analysis for causal assumptions is absent.",
                )
            )

        if not self.dag_or_equivalent_causal_structure_available:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CAUSAL_IDENTIFICATION_MISSING,
                    AdvancedValidationSeverity.MINOR,
                    "No explicit causal structure is available.",
                )
            )

        return tuple(findings)


# ============================================================================
# RARE-EVENT VALIDATION
# ============================================================================


@dataclass(frozen=True, slots=True)
class RareEventProfile:
    """
    Validation profile for low-base-rate events.

    Especially relevant to serious violence, armed conflict, major escalation,
    catastrophic infrastructure failures and other rare events.
    """

    event_count: int
    non_event_count: int

    event_definition_validated: bool
    base_rate_known: bool
    class_imbalance_assessed: bool
    rare_event_method_appropriate: bool
    calibration_performed: bool
    temporal_validation_performed: bool

    count_model: str | None = None
    overdispersion_assessed: bool = False
    zero_inflation_assessed: bool = False

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        total = self.event_count + self.non_event_count

        if total <= 0:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.EVENT_DEFINITION_MISSING,
                    AdvancedValidationSeverity.CRITICAL,
                    "No observations are available.",
                )
            )
            return tuple(findings)

        if not self.event_definition_validated:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.EVENT_DEFINITION_MISSING,
                    AdvancedValidationSeverity.CRITICAL,
                    "Outcome/event definition has not been validated.",
                )
            )

        if not self.base_rate_known:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.BASE_RATE_NEGLECT,
                    AdvancedValidationSeverity.CRITICAL,
                    "Outcome base rate is unknown.",
                )
            )

        if not self.class_imbalance_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CLASS_IMBALANCE,
                    AdvancedValidationSeverity.MAJOR,
                    "Class imbalance has not been assessed.",
                )
            )

        if not self.rare_event_method_appropriate:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.RARE_EVENT_BIAS,
                    AdvancedValidationSeverity.MAJOR,
                    "The selected method has not been demonstrated appropriate for the event prevalence.",
                )
            )

        if not self.calibration_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.RARE_EVENT_BIAS,
                    AdvancedValidationSeverity.CRITICAL,
                    "Rare-event probability estimates are uncalibrated.",
                )
            )

        if not self.temporal_validation_performed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INVALID_TEMPORAL_SPLIT,
                    AdvancedValidationSeverity.MAJOR,
                    "Rare-event model lacks temporal validation.",
                )
            )

        if self.count_model is not None:
            normalized = self.count_model.lower()

            if normalized in {"poisson", "poisson_regression"}:
                if not self.overdispersion_assessed:
                    findings.append(
                        AdvancedFinding(
                            AdvancedFindingCode.OVERDISPERSION,
                            AdvancedValidationSeverity.MAJOR,
                            "Poisson count model used without overdispersion assessment.",
                        )
                    )

            if not self.zero_inflation_assessed:
                findings.append(
                    AdvancedFinding(
                        AdvancedFindingCode.ZERO_INFLATION,
                        AdvancedValidationSeverity.MINOR,
                        "Zero inflation has not been assessed for count data.",
                    )
                )

        return tuple(findings)


# ============================================================================
# COMPLEX-SYSTEM VALIDATION
# ============================================================================


@dataclass(frozen=True, slots=True)
class ComplexSystemProfile:
    """
    Validation of dynamic-system properties.

    The purpose is not to claim that a system has a tipping point. The purpose
    is to require explicit assessment before such claims are made.
    """

    state_variable_defined: bool
    trajectory_assessed: bool
    rate_assessed: bool
    acceleration_assessed: bool

    persistence_assessed: bool
    feedback_assessed: bool
    coupling_assessed: bool
    nonlinearities_assessed: bool

    regime_change_assessed: bool
    hysteresis_assessed: bool
    critical_transition_assessed: bool
    cascade_assessed: bool

    resilience_assessed: bool
    recovery_rate_assessed: bool
    adaptive_capacity_assessed: bool

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        checks = (
            (
                not self.state_variable_defined,
                AdvancedFindingCode.COMPLEX_DYNAMICS_UNASSESSED,
                "System state is not explicitly defined.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.trajectory_assessed,
                AdvancedFindingCode.COMPLEX_DYNAMICS_UNASSESSED,
                "Trajectory has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.rate_assessed,
                AdvancedFindingCode.COMPLEX_DYNAMICS_UNASSESSED,
                "Rate of change has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.acceleration_assessed,
                AdvancedFindingCode.COMPLEX_DYNAMICS_UNASSESSED,
                "Acceleration/change in rate has not been assessed.",
                AdvancedValidationSeverity.MINOR,
            ),
            (
                not self.persistence_assessed,
                AdvancedFindingCode.COMPLEX_DYNAMICS_UNASSESSED,
                "Persistence versus transient deviation has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.feedback_assessed,
                AdvancedFindingCode.FEEDBACK_UNASSESSED,
                "Feedback loops have not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.coupling_assessed,
                AdvancedFindingCode.COMPLEX_DYNAMICS_UNASSESSED,
                "Subsystem coupling has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.nonlinearities_assessed,
                AdvancedFindingCode.COMPLEX_DYNAMICS_UNASSESSED,
                "Nonlinear behaviour has not been assessed.",
                AdvancedValidationSeverity.MINOR,
            ),
            (
                not self.regime_change_assessed,
                AdvancedFindingCode.REGIME_TRANSITION_UNASSESSED,
                "Potential regime changes have not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.hysteresis_assessed,
                AdvancedFindingCode.HYSTERESIS_UNASSESSED,
                "Hysteresis has not been assessed where relevant.",
                AdvancedValidationSeverity.MINOR,
            ),
            (
                not self.critical_transition_assessed,
                AdvancedFindingCode.CRITICAL_TRANSITION_UNASSESSED,
                "Critical-transition indicators have not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.cascade_assessed,
                AdvancedFindingCode.CASCADE_RISK_UNASSESSED,
                "Cascade propagation has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.resilience_assessed,
                AdvancedFindingCode.RESILIENCE_UNASSESSED,
                "System resilience has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.recovery_rate_assessed,
                AdvancedFindingCode.RECOVERY_CAPACITY_UNASSESSED,
                "Recovery rate has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.adaptive_capacity_assessed,
                AdvancedFindingCode.RESILIENCE_UNASSESSED,
                "Adaptive capacity has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
        )

        for condition, code, message, severity in checks:
            if condition:
                findings.append(
                    AdvancedFinding(
                        code=code,
                        severity=severity,
                        message=message,
                    )
                )

        return tuple(findings)


# ============================================================================
# CAPACITY / QUEUEING
# ============================================================================


@dataclass(frozen=True, slots=True)
class CapacityProfile:
    """
    Capacity model for systems receiving variable demand.
    """

    demand_rate: float
    service_rate: float

    nominal_capacity: float | None
    effective_capacity: float | None
    accessible_capacity: float | None
    mobilizable_capacity: float | None

    bottleneck_identified: bool
    queueing_model_selected: bool
    transient_surge_assessed: bool
    recovery_capacity_assessed: bool
    time_to_exhaustion_assessed: bool

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        values = (
            self.demand_rate,
            self.service_rate,
            self.nominal_capacity,
            self.effective_capacity,
            self.accessible_capacity,
            self.mobilizable_capacity,
        )

        for value in values:
            if value is not None and not isfinite(value):
                findings.append(
                    AdvancedFinding(
                        AdvancedFindingCode.CAPACITY_DEFINITION_MISSING,
                        AdvancedValidationSeverity.CRITICAL,
                        "Capacity or demand contains a non-finite value.",
                    )
                )

        if self.demand_rate < 0 or self.service_rate < 0:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CAPACITY_DEFINITION_MISSING,
                    AdvancedValidationSeverity.CRITICAL,
                    "Demand and service rates cannot be negative.",
                )
            )

        if not self.bottleneck_identified:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.BOTTLENECK_UNASSESSED,
                    AdvancedValidationSeverity.MAJOR,
                    "System bottleneck has not been identified.",
                )
            )

        if not self.queueing_model_selected:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.QUEUEING_MODEL_MISSING,
                    AdvancedValidationSeverity.MAJOR,
                    "Queueing behaviour has not been modelled or justified.",
                )
            )

        if not self.transient_surge_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.TRANSIENT_SURGE_UNASSESSED,
                    AdvancedValidationSeverity.MAJOR,
                    "Transient demand surge has not been assessed.",
                )
            )

        if not self.recovery_capacity_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.RECOVERY_CAPACITY_UNASSESSED,
                    AdvancedValidationSeverity.MAJOR,
                    "Recovery capacity has not been assessed.",
                )
            )

        if not self.time_to_exhaustion_assessed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.TRANSIENT_SURGE_UNASSESSED,
                    AdvancedValidationSeverity.MAJOR,
                    "Time-to-exhaustion has not been assessed.",
                )
            )

        return tuple(findings)


# ============================================================================
# SPATIAL VALIDITY
# ============================================================================


@dataclass(frozen=True, slots=True)
class SpatialValidationProfile:
    """Controls for spatial inference."""

    spatial_unit_defined: bool
    denominator_validated: bool
    spatial_autocorrelation_assessed: bool
    spatial_dependence_assessed: bool
    maup_assessed: bool
    ecological_level_validated: bool
    spatiotemporal_clustering_assessed: bool

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        checks = (
            (
                not self.spatial_unit_defined,
                AdvancedFindingCode.SPATIAL_DENOMINATOR_ERROR,
                "Spatial unit is undefined.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.denominator_validated,
                AdvancedFindingCode.SPATIAL_DENOMINATOR_ERROR,
                "Spatial denominator has not been validated.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.spatial_autocorrelation_assessed,
                AdvancedFindingCode.SPATIAL_AUTOCORRELATION,
                "Spatial autocorrelation has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.spatial_dependence_assessed,
                AdvancedFindingCode.SPATIAL_DEPENDENCE,
                "Spatial dependence has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.maup_assessed,
                AdvancedFindingCode.MAUP_RISK,
                "MAUP has not been assessed.",
                AdvancedValidationSeverity.MINOR,
            ),
            (
                not self.ecological_level_validated,
                AdvancedFindingCode.ECOLOGICAL_FALLACY,
                "Ecological-level validity has not been established.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.spatiotemporal_clustering_assessed,
                AdvancedFindingCode.SPATIOTEMPORAL_CLUSTER_UNASSESSED,
                "Spatiotemporal clustering has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
        )

        for condition, code, message, severity in checks:
            if condition:
                findings.append(
                    AdvancedFinding(code, severity, message)
                )

        return tuple(findings)


# ============================================================================
# SOURCE INDEPENDENCE
# ============================================================================


@dataclass(frozen=True, slots=True)
class SourceLineage:
    """Represents one source and its upstream provenance."""

    source_id: str
    upstream_source_ids: tuple[str, ...] = ()
    intermediary_source_ids: tuple[str, ...] = ()
    independent_origin: bool = True


def effective_independent_source_count(
    sources: Sequence[SourceLineage],
) -> int:
    """
    Estimate independent evidential origins.

    This deliberately counts upstream origin identifiers rather than
    publications. Five publications derived from the same upstream source
    therefore do not become five independent observations.
    """

    if not sources:
        return 0

    origins: set[str] = set()

    for source in sources:
        if source.upstream_source_ids:
            origins.update(source.upstream_source_ids)
        else:
            origins.add(source.source_id)

    return len(origins)


def validate_source_independence_advanced(
    sources: Sequence[SourceLineage],
    minimum_independent_sources: int,
) -> tuple[AdvancedFinding, ...]:
    findings: list[AdvancedFinding] = []

    if minimum_independent_sources < 1:
        raise ValueError("minimum_independent_sources must be >= 1")

    independent_count = effective_independent_source_count(sources)

    if independent_count < minimum_independent_sources:
        findings.append(
            AdvancedFinding(
                AdvancedFindingCode.CORROBORATION_NOT_INDEPENDENT,
                AdvancedValidationSeverity.MAJOR,
                (
                    f"Only {independent_count} independent evidential origins "
                    f"were identified; {minimum_independent_sources} required."
                ),
            )
        )

    for source in sources:
        if not source.independent_origin:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.SOURCE_COMMON_ORIGIN,
                    AdvancedValidationSeverity.MAJOR,
                    f"Source {source.source_id} is not independent.",
                    field="source_id",
                )
            )

    return tuple(findings)


# ============================================================================
# CEUTIA FEEDBACK / SELF-IMPACT
# ============================================================================


@dataclass(frozen=True, slots=True)
class FeedbackEvent:
    """
    Records an intervention or information event that may alter the monitored
    system.
    """

    event_id: str
    timestamp: datetime
    source: FeedbackSource
    intervention_id: str | None
    affected_domain: str
    affected_population_level: str
    measurable_effect_possible: bool

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        if not self.event_id.strip():
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CEUTIA_FEEDBACK,
                    AdvancedValidationSeverity.CRITICAL,
                    "Feedback event has no identifier.",
                )
            )

        if self.source is FeedbackSource.UNKNOWN:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.CEUTIA_FEEDBACK,
                    AdvancedValidationSeverity.MAJOR,
                    "Feedback origin is unknown.",
                )
            )

        if self.measurable_effect_possible and self.intervention_id is None:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INTERVENTION_NOT_REGISTERED,
                    AdvancedValidationSeverity.MAJOR,
                    "An intervention may affect the system but has no intervention identifier.",
                )
            )

        return tuple(findings)


def validate_ceutia_feedback(
    *,
    prediction_timestamp: datetime,
    observation_timestamp: datetime,
    feedback_events: Sequence[FeedbackEvent],
) -> tuple[AdvancedFinding, ...]:
    """
    Detects contamination of post-alert observations by CeutIA intervention.

    This does not discard those observations. It changes their epistemic role.
    """

    findings: list[AdvancedFinding] = []

    for event in feedback_events:
        findings.extend(event.validate())

        if (
            event.source
            in {
                FeedbackSource.CEUTIA_PUBLIC_OUTPUT,
                FeedbackSource.CEUTIA_ALERT,
                FeedbackSource.CEUTIA_RECOMMENDATION,
                FeedbackSource.HUMAN_DECISION_AFTER_CEUTIA,
            }
            and event.timestamp <= observation_timestamp
            and event.timestamp >= prediction_timestamp
        ):
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INTERVENTION_CONTAMINATION,
                    AdvancedValidationSeverity.MAJOR,
                    (
                        "Observation occurred after a CeutIA-related intervention "
                        "and may therefore contain system-induced behavioural effects."
                    ),
                    remediation=(
                        "Register the intervention and model the feedback pathway "
                        "instead of treating the observation as fully exogenous."
                    ),
                )
            )

    return tuple(findings)


# ============================================================================
# HYPOTHESIS / SCENARIO VALIDATION
# ============================================================================


@dataclass(frozen=True, slots=True)
class HypothesisProfile:
    """Formal structure for competing hypotheses."""

    hypothesis_id: str
    description: str

    falsifiable: bool
    assumptions: tuple[str, ...]
    differentiating_predictions: tuple[str, ...]
    evidence_for: tuple[str, ...]
    evidence_against: tuple[str, ...]

    competing_hypothesis_ids: tuple[str, ...] = ()
    counterfactual_defined: bool = False

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        if not self.falsifiable:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.SCENARIO_NOT_FALSIFIABLE,
                    AdvancedValidationSeverity.CRITICAL,
                    f"Hypothesis {self.hypothesis_id} is not falsifiable.",
                )
            )

        if not self.assumptions:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.SCENARIO_ASSUMPTION_MISSING,
                    AdvancedValidationSeverity.MAJOR,
                    f"Hypothesis {self.hypothesis_id} has no explicit assumptions.",
                )
            )

        if not self.differentiating_predictions:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.COMPETING_HYPOTHESES_MISSING,
                    AdvancedValidationSeverity.MAJOR,
                    (
                        f"Hypothesis {self.hypothesis_id} has no "
                        "differentiating predictions."
                    ),
                )
            )

        if not self.competing_hypothesis_ids:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.COMPETING_HYPOTHESES_MISSING,
                    AdvancedValidationSeverity.MAJOR,
                    (
                        f"Hypothesis {self.hypothesis_id} has no "
                        "explicit competing hypotheses."
                    ),
                )
            )

        if not self.counterfactual_defined:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.COUNTERFACTUAL_UNDEFINED,
                    AdvancedValidationSeverity.MINOR,
                    f"Hypothesis {self.hypothesis_id} has no explicit counterfactual.",
                )
            )

        return tuple(findings)


# ============================================================================
# ADVERSARIAL AI / LLM VALIDATION
# ============================================================================


@dataclass(frozen=True, slots=True)
class AIAdversarialProfile:
    """
    Security profile for LLM/ML components operating over external data.
    """

    prompt_injection_tested: bool
    indirect_prompt_injection_tested: bool
    instruction_hijacking_tested: bool

    poisoned_data_tested: bool
    fabricated_evidence_tested: bool

    model_extraction_risk_assessed: bool
    membership_inference_risk_assessed: bool
    model_inversion_risk_assessed: bool

    output_oracle_risk_assessed: bool
    automation_bias_assessed: bool

    citations_machine_verified: bool
    tool_permissions_least_privilege: bool
    untrusted_content_isolated: bool

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        checks = (
            (
                not self.prompt_injection_tested,
                AdvancedFindingCode.PROMPT_INJECTION,
                "Direct prompt-injection resistance has not been tested.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.indirect_prompt_injection_tested,
                AdvancedFindingCode.INDIRECT_PROMPT_INJECTION,
                "Indirect prompt-injection resistance has not been tested.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.instruction_hijacking_tested,
                AdvancedFindingCode.INSTRUCTION_HIJACKING,
                "Instruction-hijacking resistance has not been tested.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.poisoned_data_tested,
                AdvancedFindingCode.DATA_POISONING_AI,
                "AI data-poisoning resistance has not been tested.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.fabricated_evidence_tested,
                AdvancedFindingCode.FABRICATED_EVIDENCE,
                "Fabricated-evidence resistance has not been tested.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.model_extraction_risk_assessed,
                AdvancedFindingCode.MODEL_EXTRACTION,
                "Model-extraction risk has not been assessed.",
                AdvancedValidationSeverity.MINOR,
            ),
            (
                not self.membership_inference_risk_assessed,
                AdvancedFindingCode.MEMBERSHIP_INFERENCE,
                "Membership-inference risk has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.model_inversion_risk_assessed,
                AdvancedFindingCode.MODEL_INVERSION,
                "Model-inversion risk has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.output_oracle_risk_assessed,
                AdvancedFindingCode.OUTPUT_ORACLE,
                "Output-oracle risk has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.automation_bias_assessed,
                AdvancedFindingCode.AUTOMATION_BIAS,
                "Automation-bias risk has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.citations_machine_verified,
                AdvancedFindingCode.FABRICATED_EVIDENCE,
                "Citations are not machine-verified.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.tool_permissions_least_privilege,
                AdvancedFindingCode.INSTRUCTION_HIJACKING,
                "Tool permissions do not satisfy least privilege.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.untrusted_content_isolated,
                AdvancedFindingCode.INDIRECT_PROMPT_INJECTION,
                "Untrusted external content is not isolated from instructions.",
                AdvancedValidationSeverity.CRITICAL,
            ),
        )

        for condition, code, message, severity in checks:
            if condition:
                findings.append(
                    AdvancedFinding(code, severity, message)
                )

        return tuple(findings)


# ============================================================================
# INTERVENTION EVALUATION
# ============================================================================


@dataclass(frozen=True, slots=True)
class InterventionEvaluation:
    """
    Formal record of what happened after a CeutIA-supported intervention.
    """

    intervention_id: str
    intervention_timestamp: datetime
    outcome_window_start: datetime
    outcome_window_end: datetime

    target_outcome_defined: bool
    baseline_defined: bool
    comparator_defined: bool

    adverse_effects_assessed: bool
    unintended_effects_assessed: bool
    contamination_by_ceutia_assessed: bool

    observed_outcome: float | None = None

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        if self.outcome_window_start < self.intervention_timestamp:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INVALID_TEMPORAL_SPLIT,
                    AdvancedValidationSeverity.CRITICAL,
                    "Outcome window starts before intervention.",
                )
            )

        if self.outcome_window_end <= self.outcome_window_start:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.INVALID_TEMPORAL_SPLIT,
                    AdvancedValidationSeverity.CRITICAL,
                    "Outcome window is invalid.",
                )
            )

        checks = (
            (
                not self.target_outcome_defined,
                AdvancedFindingCode.OUTCOME_NOT_REGISTERED,
                "Target outcome is not defined.",
                AdvancedValidationSeverity.CRITICAL,
            ),
            (
                not self.baseline_defined,
                AdvancedFindingCode.IMPACT_NOT_ASSESSED,
                "Baseline is not defined.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.comparator_defined,
                AdvancedFindingCode.IMPACT_NOT_ASSESSED,
                "Comparator or counterfactual is not defined.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.adverse_effects_assessed,
                AdvancedFindingCode.IMPACT_NOT_ASSESSED,
                "Adverse effects have not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.unintended_effects_assessed,
                AdvancedFindingCode.IMPACT_NOT_ASSESSED,
                "Unintended effects have not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
            (
                not self.contamination_by_ceutia_assessed,
                AdvancedFindingCode.INTERVENTION_CONTAMINATION,
                "CeutIA-induced behavioural contamination has not been assessed.",
                AdvancedValidationSeverity.MAJOR,
            ),
        )

        for condition, code, message, severity in checks:
            if condition:
                findings.append(
                    AdvancedFinding(code, severity, message)
                )

        return tuple(findings)


# ============================================================================
# EPISTEMIC FIREWALL
# ============================================================================


@dataclass(frozen=True, slots=True)
class EpistemicRecord:
    """
    Immutable epistemic record.

    A record can identify where a conclusion came from, but its own existence
    cannot be counted as independent evidence.
    """

    record_id: str
    record_type: str

    source_record_ids: tuple[str, ...] = ()
    derived_from_record_ids: tuple[str, ...] = ()

    independently_observed: bool = False
    externally_validated: bool = False
    generated_by_ceutia: bool = False

    evidential_weight: float = 0.0

    def validate(self) -> tuple[AdvancedFinding, ...]:
        findings: list[AdvancedFinding] = []

        if self.generated_by_ceutia and self.independently_observed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.EPISTEMIC_SELF_CONFIRMATION,
                    AdvancedValidationSeverity.CRITICAL,
                    (
                        "A CeutIA-generated record cannot simultaneously "
                        "be treated as an independent observation."
                    ),
                )
            )

        if self.generated_by_ceutia and self.external_validated is False:
            # No finding merely because a record is generated internally.
            # Internal generation is legitimate; independent evidential status
            # is the protected property.
            pass

        if self.evidential_weight < 0:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.EPISTEMIC_SELF_CONFIRMATION,
                    AdvancedValidationSeverity.CRITICAL,
                    "Evidential weight cannot be negative.",
                )
            )

        return tuple(findings)


def validate_epistemic_firewall(
    records: Sequence[EpistemicRecord],
) -> tuple[AdvancedFinding, ...]:
    """
    Prevents recursive evidence inflation.

    If A is derived from B, A cannot be counted as independent corroboration
    of B. Likewise, a CeutIA prediction cannot corroborate itself merely because
    it was later emitted as an alert.
    """

    findings: list[AdvancedFinding] = []

    record_ids = {record.record_id for record in records}

    for record in records:
        findings.extend(record.validate())

        for dependency in record.derived_from_record_ids:
            if dependency == record.record_id:
                findings.append(
                    AdvancedFinding(
                        AdvancedFindingCode.EPISTEMIC_SELF_CONFIRMATION,
                        AdvancedValidationSeverity.CRITICAL,
                        f"Record {record.record_id} is self-derived.",
                    )
                )

            if dependency not in record_ids:
                findings.append(
                    AdvancedFinding(
                        AdvancedFindingCode.SOURCE_LINEAGE_UNKNOWN,
                        AdvancedValidationSeverity.MAJOR,
                        (
                            f"Record {record.record_id} references unknown "
                            f"dependency {dependency}."
                        ),
                    )
                )

    for record in records:
        if not record.generated_by_ceutia:
            continue

        if record.independently_observed:
            findings.append(
                AdvancedFinding(
                    AdvancedFindingCode.EPISTEMIC_SELF_CONFIRMATION,
                    AdvancedValidationSeverity.CRITICAL,
                    (
                        f"CeutIA-generated record {record.record_id} "
                        "is incorrectly marked independent."
                    ),
                )
            )

    return tuple(findings)


# ============================================================================
# NUMERICAL SAFETY HELPERS
# ============================================================================


def safe_rate(
    numerator: float,
    denominator: float,
) -> float:
    """
    Compute a rate while refusing silent division by zero.

    This function does not assign a zero risk to an undefined rate.
    """

    if not isfinite(numerator) or not isfinite(denominator):
        raise ValueError("Numerator and denominator must be finite.")

    if denominator <= 0:
        raise ValueError(
            "Rate denominator must be strictly positive."
        )

    result = numerator / denominator

    if not isfinite(result):
        raise ValueError("Computed rate is not finite.")

    return result


def utilization_ratio(
    demand: float,
    capacity: float,
) -> float:
    """
    Demand/capacity ratio.

    Values > 1 are valid and represent overload.
    """

    if not isfinite(demand) or not isfinite(capacity):
        raise ValueError("Demand and capacity must be finite.")

    if demand < 0:
        raise ValueError("Demand cannot be negative.")

    if capacity <= 0:
        raise ValueError("Capacity must be strictly positive.")

    return demand / capacity


def exponential_growth_rate(
    initial: float,
    final: float,
    elapsed_time: float,
) -> float:
    """
    Continuous growth rate:

        r = ln(final / initial) / Δt

    No value is returned for non-positive population/count states because the
    logarithmic model is undefined there.
    """

    if initial <= 0 or final <= 0:
        raise ValueError(
            "Initial and final values must be strictly positive."
        )

    if elapsed_time <= 0:
        raise ValueError(
            "Elapsed time must be strictly positive."
        )

    return log(final / initial) / elapsed_time


# ============================================================================
# ADVANCED VALIDATION ORCHESTRATOR
# ============================================================================


@dataclass(frozen=True, slots=True)
class AdvancedValidationReport:
    """Aggregated result of the advanced validation layer."""

    findings: tuple[AdvancedFinding, ...]
    generated_at: datetime

    @property
    def critical_count(self) -> int:
        return sum(
            finding.severity is AdvancedValidationSeverity.CRITICAL
            for finding in self.findings
        )

    @property
    def major_count(self) -> int:
        return sum(
            finding.severity is AdvancedValidationSeverity.MAJOR
            for finding in self.findings
        )

    @property
    def blocked(self) -> bool:
        return self.critical_count > 0

    @property
    def shadow_only(self) -> bool:
        return not self.blocked and self.major_count > 0

    @property
    def operationally_eligible(self) -> bool:
        return not self.blocked and not self.shadow_only

    def by_code(
        self,
        code: AdvancedFindingCode,
    ) -> tuple[AdvancedFinding, ...]:
        return tuple(
            finding
            for finding in self.findings
            if finding.code is code
        )


def run_advanced_validation(
    *,
    data_integrity: DataIntegrityProfile | None = None,
    temporal: TemporalValidationProfile | None = None,
    causal: CausalValidityProfile | None = None,
    rare_event: RareEventProfile | None = None,
    complex_system: ComplexSystemProfile | None = None,
    capacity: CapacityProfile | None = None,
    spatial: SpatialValidationProfile | None = None,
    sources: Sequence[SourceLineage] = (),
    minimum_independent_sources: int | None = None,
    feedback_events: Sequence[FeedbackEvent] = (),
    prediction_timestamp: datetime | None = None,
    observation_timestamp: datetime | None = None,
    hypotheses: Sequence[HypothesisProfile] = (),
    ai_security: AIAdversarialProfile | None = None,
    intervention: InterventionEvaluation | None = None,
    epistemic_records: Sequence[EpistemicRecord] = (),
) -> AdvancedValidationReport:
    """
    Run all supplied advanced validators.

    Omitted profiles are not treated as valid. They simply mean that the
    corresponding validation layer was not requested in this invocation.

    This permits staged execution while keeping each supplied profile strict.
    """

    findings: list[AdvancedFinding] = []

    if data_integrity is not None:
        findings.extend(data_integrity.validate())

    if temporal is not None:
        findings.extend(temporal.validate())

    if causal is not None:
        findings.extend(causal.validate())

    if rare_event is not None:
        findings.extend(rare_event.validate())

    if complex_system is not None:
        findings.extend(complex_system.validate())

    if capacity is not None:
        findings.extend(capacity.validate())

    if spatial is not None:
        findings.extend(spatial.validate())

    if minimum_independent_sources is not None:
        findings.extend(
            validate_source_independence_advanced(
                sources,
                minimum_independent_sources,
            )
        )

    if (
        prediction_timestamp is not None
        and observation_timestamp is not None
    ):
        findings.extend(
            validate_ceutia_feedback(
                prediction_timestamp=prediction_timestamp,
                observation_timestamp=observation_timestamp,
                feedback_events=feedback_events,
            )
        )
    elif feedback_events:
        findings.append(
            AdvancedFinding(
                AdvancedFindingCode.CEUTIA_FEEDBACK,
                AdvancedValidationSeverity.MAJOR,
                (
                    "Feedback events were supplied without prediction and "
                    "observation timestamps."
                ),
            )
        )

    for hypothesis in hypotheses:
        findings.extend(hypothesis.validate())

    if ai_security is not None:
        findings.extend(ai_security.validate())

    if intervention is not None:
        findings.extend(intervention.validate())

    if epistemic_records:
        findings.extend(
            validate_epistemic_firewall(epistemic_records)
        )

    return AdvancedValidationReport(
        findings=tuple(findings),
        generated_at=datetime.utcnow(),
    )


# ============================================================================
# HARD OPERATIONAL GATE
# ============================================================================


def assert_advanced_operational_eligibility(
    report: AdvancedValidationReport,
) -> None:
    """
    Fail closed.

    Advanced findings marked CRITICAL or MAJOR prevent operational
    authorization.

    A future policy layer may explicitly permit SHADOW_ONLY use, but this
    function never silently promotes a partially validated capability.
    """

    if report.critical_count:
        raise RuntimeError(
            "CeutIA capability BLOCKED: "
            f"{report.critical_count} critical advanced validation findings."
        )

    if report.major_count:
        raise RuntimeError(
            "CeutIA capability NOT OPERATIONALLY ELIGIBLE: "
            f"{report.major_count} major advanced validation findings."
        )


# ============================================================================
# ADVANCED SCIENTIFIC INVARIANTS
# ============================================================================


ADVANCED_SCIENTIFIC_INVARIANTS: tuple[str, ...] = (
    "No dataset is considered truthful merely because it has passed a parser.",
    "Provenance is part of the evidence, not optional metadata.",
    "Publication count is not independent-source count.",
    "Temporal leakage invalidates predictive evaluation.",
    "Knowledge time must be distinguished from world time.",
    "Post-outcome information cannot enter a historical prediction.",
    "Association is not causation.",
    "Temporal precedence alone does not establish causality.",
    "Causal claims require an explicit identification strategy.",
    "Rare-event probability requires base-rate awareness and calibration.",
    "A high AUC does not establish calibration or operational utility.",
    "A low Brier score does not establish causal validity.",
    "Spatial observations are not independent merely because they have different coordinates.",
    "Population-level associations cannot automatically be applied to individuals.",
    "A complex system must be analysed through state and trajectory, not isolated values alone.",
    "A tipping point must never be declared merely because a threshold was crossed.",
    "A threshold is not a phase transition unless the evidence supports that interpretation.",
    "Capacity must distinguish nominal, effective, accessible and mobilizable capacity.",
    "Demand greater than capacity is not itself proof of system collapse.",
    "CeutIA-generated alerts cannot be counted as independent evidence.",
    "CeutIA interventions can alter the data-generating process.",
    "Post-intervention observations require feedback-aware interpretation.",
    "A model-generated hypothesis cannot validate itself.",
    "A scenario must not be presented as a prediction unless predictive validation exists.",
    "Competing hypotheses must remain possible when evidence does not discriminate between them.",
    "LLM output is not evidence merely because it is fluent.",
    "LLMs must not fabricate citations, observations or measurements.",
    "Untrusted external content must never override system instructions or security policy.",
    "External content must be treated as data, not instructions.",
    "Security controls cannot depend on the model correctly interpreting malicious content.",
    "Automation must fail closed when epistemic requirements are unmet.",
    "No individual dangerousness score may be inferred from nationality, ethnicity, religion, migration status or other protected characteristics.",
    "System-level security signals must not be transformed into individual criminality predictions.",
    "Violence detection concerns observable events and escalation signals, not inherent group properties.",
    "Uncertainty must be preserved through every transformation.",
    "Unknown is a valid epistemic state.",
    "Absence of evidence is not evidence of absence unless the observation process supports that inference.",
    "CeutIA must preserve the history of how every operational conclusion was reached.",
)


def validate_advanced_invariants() -> None:
    """Static integrity check for the advanced invariant registry."""

    if len(ADVANCED_SCIENTIFIC_INVARIANTS) < 30:
        raise RuntimeError(
            "Advanced scientific invariant registry is unexpectedly incomplete."
        )

    if len(set(ADVANCED_SCIENTIFIC_INVARIANTS)) != len(
        ADVANCED_SCIENTIFIC_INVARIANTS
    ):
        raise RuntimeError(
            "Advanced scientific invariant registry contains duplicates."
        )


validate_advanced_invariants()"""
CeutIA — Adversarial Validation Gate
====================================

Sistema de validación adversarial multidisciplinar para CeutIA.

Propósito
---------
Este módulo convierte las seis perspectivas expertas de revisión de CeutIA
en controles ejecutables. Su función no es demostrar que un modelo "funciona",
sino intentar encontrar condiciones bajo las cuales sus resultados dejan de ser
fiables, interpretables, útiles o admisibles.

Los seis dominios de revisión son:

1. Strategic intelligence / OSINT
2. Operational security / emergency management
3. Epidemiology / public health
4. Geospatial / border / population analysis
5. Technology law / privacy / cybersecurity
6. Statistics / ML / predictive validation

Principio rector
---------------
Una capacidad predictiva no se considera operacionalmente válida porque:

- produzca una puntuación;
- tenga una métrica favorable;
- utilice machine learning;
- combine muchas fuentes;
- produzca alertas plausibles;
- o coincida retrospectivamente con algunos acontecimientos.

Debe superar controles independientes sobre:

    provenance
    independence
    corroboration
    contradiction
    temporal validity
    spatial validity
    uncertainty
    calibration
    discrimination
    false positives
    false negatives
    lead time
    utility
    drift
    missingness
    subgroup robustness
    privacy
    security
    human oversight
    reproducibility

Este módulo NO autoriza vigilancia individual ni predicción de peligrosidad
individual o colectiva basada en nacionalidad, origen u otros atributos
protegidos.

La unidad primaria de predicción de seguridad debe ser un fenómeno observable
del sistema, evento, flujo, infraestructura o entorno, no la identidad de una
persona o grupo.

Arquitectura de decisión
------------------------

    candidate
        |
        v
    six-domain validation
        |
        +---- critical failure ----> BLOCK
        |
        +---- major unresolved ----> SHADOW_ONLY
        |
        +---- all mandatory gates ----> PASS
        |
        v
    operational eligibility

"SHADOW_ONLY" significa que el componente puede ejecutarse para evaluación
retrospectiva/prospectiva sin que su salida pueda activar decisiones
operacionales.

Diseño
------
- stdlib only;
- immutable result objects;
- fail-closed;
- deterministic;
- auditable;
- no acceso a bases de datos;
- no acceso a red;
- no ejecución de modelos;
- no inferencia automática de identidad;
- no decisión operativa.

El módulo valida las condiciones bajo las cuales otro componente puede ser
considerado apto para operar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from math import isfinite
from typing import Final, Mapping, Sequence


class ValidationDecision(str, Enum):
    """Resultado final del gate adversarial."""

    PASS = "pass"
    SHADOW_ONLY = "shadow_only"
    BLOCK = "block"


class FindingSeverity(str, Enum):
    """Severidad de una deficiencia encontrada durante la validación."""

    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ExpertDomain(str, Enum):
    """Los seis dominios expertos que deben poder auditar CeutIA."""

    STRATEGIC_INTELLIGENCE = "strategic_intelligence"
    OPERATIONAL_SECURITY = "operational_security"
    EPIDEMIOLOGY_PUBLIC_HEALTH = "epidemiology_public_health"
    GEOSPATIAL_POPULATION = "geospatial_population"
    LAW_PRIVACY_CYBERSECURITY = "law_privacy_cybersecurity"
    STATISTICS_ML = "statistics_ml"


class ValidationDimension(str, Enum):
    """Dimensiones transversales examinadas por los expertos."""

    PROVENANCE = "provenance"
    SOURCE_INDEPENDENCE = "source_independence"
    CORROBORATION = "corroboration"
    CONTRADICTION = "contradiction"
    TEMPORAL_VALIDITY = "temporal_validity"
    SPATIAL_VALIDITY = "spatial_validity"
    EPISTEMIC_SEPARATION = "epistemic_separation"
    UNCERTAINTY = "uncertainty"
    CALIBRATION = "calibration"
    DISCRIMINATION = "discrimination"
    FALSE_POSITIVES = "false_positives"
    FALSE_NEGATIVES = "false_negatives"
    LEAD_TIME = "lead_time"
    OPERATIONAL_UTILITY = "operational_utility"
    MISSINGNESS = "missingness"
    DRIFT = "drift"
    ROBUSTNESS = "robustness"
    SUBGROUP_ROBUSTNESS = "subgroup_robustness"
    PRIVACY = "privacy"
    SECURITY = "security"
    HUMAN_OVERSIGHT = "human_oversight"
    REPRODUCIBILITY = "reproducibility"
    IDENTITY_INFERENCE = "identity_inference"
    AUTOMATED_ACTION = "automated_action"


class TargetLevel(str, Enum):
    """
    Unidad sobre la que opera la capacidad evaluada.

    SYSTEM:
        territorio, infraestructura, capacidad, flujo o sistema.

    EVENT:
        acontecimiento observable.

    POPULATION:
        agregado poblacional.

    INDIVIDUAL:
        persona identificable o potencialmente identificable.

    GROUP:
        colectivo definido por identidad/procedencia/atributos.

    CeutIA puede analizar sistemas, eventos y agregados.
    La predicción de peligrosidad individual/grupal requiere un gate
    explícito y queda bloqueada por defecto.
    """

    SYSTEM = "system"
    EVENT = "event"
    POPULATION = "population"
    INDIVIDUAL = "individual"
    GROUP = "group"


class EvidenceMaturity(str, Enum):
    """Madurez de la evidencia que sustenta una capacidad."""

    UNASSESSED = "unassessed"
    EXPLORATORY = "exploratory"
    RETROSPECTIVELY_VALIDATED = "retrospectively_validated"
    TEMPORALLY_VALIDATED = "temporally_validated"
    EXTERNALLY_VALIDATED = "externally_validated"
    PROSPECTIVELY_VALIDATED = "prospectively_validated"


class DataUseMode(str, Enum):
    """Modo de utilización de datos."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    RESTRICTED = "restricted"


class FindingCode(str, Enum):
    """Códigos normalizados para problemas detectados."""

    MISSING_PROVENANCE = "missing_provenance"
    DEPENDENT_SOURCES = "dependent_sources"
    INSUFFICIENT_CORROBORATION = "insufficient_corroboration"
    UNRESOLVED_CONTRADICTION = "unresolved_contradiction"
    NO_TEMPORAL_VALIDATION = "no_temporal_validation"
    NO_SPATIAL_VALIDATION = "no_spatial_validation"
    EPISTEMIC_COLLAPSE = "epistemic_collapse"
    UNCERTAINTY_MISSING = "uncertainty_missing"
    UNCALIbrATED_PROBABILITY = "uncalibrated_probability"
    DISCRIMINATION_UNASSESSED = "discrimination_unassessed"
    FALSE_POSITIVE_COST_UNKNOWN = "false_positive_cost_unknown"
    FALSE_NEGATIVE_COST_UNKNOWN = "false_negative_cost_unknown"
    LEAD_TIME_UNKNOWN = "lead_time_unknown"
    UTILITY_UNASSESSED = "utility_unassessed"
    MISSINGNESS_UNASSESSED = "missingness_unassessed"
    DRIFT_UNASSESSED = "drift_unassessed"
    ROBUSTNESS_UNASSESSED = "robustness_unassessed"
    SUBGROUP_ROBUSTNESS_UNASSESSED = "subgroup_robustness_unassessed"
    PRIVACY_VIOLATION = "privacy_violation"
    SECURITY_VIOLATION = "security_violation"
    HUMAN_OVERSIGHT_MISSING = "human_oversight_missing"
    REPRODUCIBILITY_MISSING = "reproducibility_missing"
    IDENTITY_BASED_INFERENCE = "identity_based_inference"
    AUTOMATED_OPERATIONAL_ACTION = "automated_operational_action"
    INDIVIDUAL_DANGEROUSNESS = "individual_dangerousness"
    GROUP_DANGEROUSNESS = "group_dangerousness"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    INVALID_TARGET = "invalid_target"
    INVALID_THRESHOLD = "invalid_threshold"
    OUTCOME_UNDEFINED = "outcome_undefined"
    HORIZON_UNDEFINED = "horizon_undefined"


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """Hallazgo individual producido por un gate."""

    code: FindingCode
    severity: FindingSeverity
    domain: ExpertDomain
    dimension: ValidationDimension
    message: str
    evidence: tuple[str, ...] = ()
    remediation: str | None = None


@dataclass(frozen=True, slots=True)
class ExpertGateResult:
    """Resultado de un dominio experto."""

    domain: ExpertDomain
    passed: bool
    findings: tuple[ValidationFinding, ...] = ()

    @property
    def critical_count(self) -> int:
        return sum(
            finding.severity is FindingSeverity.CRITICAL
            for finding in self.findings
        )

    @property
    def major_count(self) -> int:
        return sum(
            finding.severity is FindingSeverity.MAJOR
            for finding in self.findings
        )


@dataclass(frozen=True, slots=True)
class ValidationDataset:
    """
    Describe el conjunto utilizado para validar una capacidad.

    No contiene los datos. Solo registra las propiedades necesarias para
    determinar si el proceso de validación es suficientemente fuerte.
    """

    dataset_id: str
    sample_size: int
    positive_events: int
    negative_events: int
    temporal_split: bool
    external_dataset: bool
    prospective_evaluation: bool
    independent_test_set: bool
    missingness_assessed: bool
    subgroup_evaluation: bool
    drift_assessed: bool

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []

        if not self.dataset_id.strip():
            errors.append("dataset_id must not be empty")

        if self.sample_size <= 0:
            errors.append("sample_size must be positive")

        if self.positive_events < 0 or self.negative_events < 0:
            errors.append("event counts must not be negative")

        if self.positive_events + self.negative_events > self.sample_size:
            errors.append("event counts cannot exceed sample_size")

        return tuple(errors)


@dataclass(frozen=True, slots=True)
class PredictivePerformance:
    """
    Rendimiento predictivo observado.

    Los campos son opcionales porque no todos los modelos necesitan todas
    las métricas. Sin embargo, los gates correspondientes exigirán las que
    sean necesarias para el tipo de capacidad evaluada.
    """

    roc_auc: float | None = None
    pr_auc: float | None = None
    brier_score: float | None = None
    calibration_in_the_large: float | None = None
    calibration_slope: float | None = None
    sensitivity: float | None = None
    specificity: float | None = None
    false_positive_rate: float | None = None
    false_negative_rate: float | None = None
    decision_curve_net_benefit: float | None = None
    lead_time_minutes: float | None = None

    def validate_ranges(self) -> tuple[str, ...]:
        errors: list[str] = []

        bounded = {
            "roc_auc": self.roc_auc,
            "pr_auc": self.pr_auc,
            "brier_score": self.brier_score,
            "sensitivity": self.sensitivity,
            "specificity": self.specificity,
            "false_positive_rate": self.false_positive_rate,
            "false_negative_rate": self.false_negative_rate,
        }

        for name, value in bounded.items():
            if value is None:
                continue

            if not isfinite(value):
                errors.append(f"{name} must be finite")

            if not 0.0 <= value <= 1.0:
                errors.append(f"{name} must be between 0 and 1")

        if self.calibration_slope is not None and not isfinite(
            self.calibration_slope
        ):
            errors.append("calibration_slope must be finite")

        if self.calibration_in_the_large is not None and not isfinite(
            self.calibration_in_the_large
        ):
            errors.append("calibration_in_the_large must be finite")

        if self.decision_curve_net_benefit is not None and not isfinite(
            self.decision_curve_net_benefit
        ):
            errors.append("decision_curve_net_benefit must be finite")

        if self.lead_time_minutes is not None:
            if not isfinite(self.lead_time_minutes):
                errors.append("lead_time_minutes must be finite")
            elif self.lead_time_minutes < 0:
                errors.append("lead_time_minutes must not be negative")

        return tuple(errors)


@dataclass(frozen=True, slots=True)
class CandidateCapability:
    """
    Especificación de una capacidad que quiere pasar a producción.

    Esta estructura describe el objeto que será atacado por los seis gates.
    """

    capability_id: str
    name: str
    target_level: TargetLevel
    data_mode: DataUseMode
    evidence_maturity: EvidenceMaturity

    scientific_references: tuple[str, ...] = ()
    provenance_complete: bool = False
    source_independence_assessed: bool = False
    corroboration_assessed: bool = False
    contradiction_handling: bool = False

    temporal_validation: bool = False
    spatial_validation: bool = False
    uncertainty_quantified: bool = False
    epistemic_separation: bool = False

    produces_probability: bool = False
    calibration_assessed: bool = False
    discrimination_assessed: bool = False
    false_positive_cost_assessed: bool = False
    false_negative_cost_assessed: bool = False
    lead_time_assessed: bool = False
    operational_utility_assessed: bool = False

    missingness_assessed: bool = False
    drift_assessed: bool = False
    robustness_assessed: bool = False
    subgroup_robustness_assessed: bool = False

    privacy_reviewed: bool = False
    cybersecurity_reviewed: bool = False
    human_oversight_required: bool = True
    human_oversight_implemented: bool = False
    reproducibility_verified: bool = False

    uses_identity_attributes: bool = False
    predicts_individual_dangerousness: bool = False
    predicts_group_dangerousness: bool = False
    automated_operational_action: bool = False

    event_definition: str | None = None
    prediction_horizon_minutes: float | None = None
    threshold_definition: str | None = None

    validation_dataset: ValidationDataset | None = None
    performance: PredictivePerformance | None = None

    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AdversarialValidationReport:
    """Informe completo producido por el proceso adversarial."""

    capability_id: str
    decision: ValidationDecision
    generated_at: datetime

    expert_results: tuple[ExpertGateResult, ...]
    findings: tuple[ValidationFinding, ...]

    mandatory_failures: tuple[FindingCode, ...]
    unresolved_major_failures: tuple[FindingCode, ...]

    @property
    def passed(self) -> bool:
        return self.decision is ValidationDecision.PASS

    @property
    def blocked(self) -> bool:
        return self.decision is ValidationDecision.BLOCK

    @property
    def shadow_only(self) -> bool:
        return self.decision is ValidationDecision.SHADOW_ONLY


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def _finding(
    code: FindingCode,
    severity: FindingSeverity,
    domain: ExpertDomain,
    dimension: ValidationDimension,
    message: str,
    *,
    evidence: Sequence[str] = (),
    remediation: str | None = None,
) -> ValidationFinding:
    return ValidationFinding(
        code=code,
        severity=severity,
        domain=domain,
        dimension=dimension,
        message=message,
        evidence=tuple(evidence),
        remediation=remediation,
    )


def _missing(
    condition: bool,
    *,
    code: FindingCode,
    severity: FindingSeverity,
    domain: ExpertDomain,
    dimension: ValidationDimension,
    message: str,
    remediation: str,
) -> ValidationFinding | None:
    if condition:
        return None

    return _finding(
        code,
        severity,
        domain,
        dimension,
        message,
        remediation=remediation,
    )


def _validate_dataset(
    candidate: CandidateCapability,
    domain: ExpertDomain,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []

    dataset = candidate.validation_dataset

    if dataset is None:
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.REPRODUCIBILITY,
                "No validation dataset has been declared.",
                remediation=(
                    "Declare the dataset, event counts, temporal split and "
                    "validation strategy."
                ),
            )
        )
        return findings

    for error in dataset.validate():
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.REPRODUCIBILITY,
                error,
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Gate 1 — Strategic intelligence / OSINT
# ---------------------------------------------------------------------------


def validate_strategic_intelligence(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa si una capacidad puede distinguir información de señal.

    Particular atención a:

    - ruido digital;
    - dependencia entre fuentes;
    - corroboración;
    - contradicciones;
    - temporalidad;
    - desinformación;
    - señales débiles;
    - separación entre existencia de contenido y verdad de su afirmación.
    """

    domain = ExpertDomain.STRATEGIC_INTELLIGENCE
    findings: list[ValidationFinding] = []

    required = (
        (
            candidate.provenance_complete,
            FindingCode.MISSING_PROVENANCE,
            ValidationDimension.PROVENANCE,
            "Source provenance is incomplete.",
            "Register source, acquisition time, transformation lineage and integrity.",
        ),
        (
            candidate.source_independence_assessed,
            FindingCode.DEPENDENT_SOURCES,
            ValidationDimension.SOURCE_INDEPENDENCE,
            "Source independence has not been assessed.",
            "Assess common-origin, syndication and coordinated-source dependency.",
        ),
        (
            candidate.corroboration_assessed,
            FindingCode.INSUFFICIENT_CORROBORATION,
            ValidationDimension.CORROBORATION,
            "Corroboration has not been assessed.",
            "Evaluate independent corroboration rather than source count.",
        ),
        (
            candidate.contradiction_handling,
            FindingCode.UNRESOLVED_CONTRADICTION,
            ValidationDimension.CONTRADICTION,
            "Contradictory observations are not explicitly represented.",
            "Preserve contradictions and expose their effect on confidence.",
        ),
        (
            candidate.temporal_validation,
            FindingCode.NO_TEMPORAL_VALIDATION,
            ValidationDimension.TEMPORAL_VALIDITY,
            "Temporal validity has not been demonstrated.",
            "Evaluate performance on future periods not used for model fitting.",
        ),
        (
            candidate.epistemic_separation,
            FindingCode.EPISTEMIC_COLLAPSE,
            ValidationDimension.EPISTEMIC_SEPARATION,
            "Epistemic states are not explicitly separated.",
            "Separate observation, signal, inference, hypothesis, prediction and scenario.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.uses_identity_attributes:
        findings.append(
            _finding(
                FindingCode.IDENTITY_BASED_INFERENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "Identity attributes are used as predictive risk features.",
                remediation=(
                    "Replace identity-based predictors with validated "
                    "observable system/event variables and document the causal "
                    "or predictive justification."
                ),
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 2 — Operational security / emergency management
# ---------------------------------------------------------------------------


def validate_operational_security(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa utilidad operacional y coste de error.

    Una alerta sin horizonte temporal, sin outcome definido o sin evaluación
    de falsos positivos/falsos negativos no se considera operacionalmente
    madura.
    """

    domain = ExpertDomain.OPERATIONAL_SECURITY
    findings: list[ValidationFinding] = []

    if not candidate.event_definition:
        findings.append(
            _finding(
                FindingCode.OUTCOME_UNDEFINED,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.OPERATIONAL_UTILITY,
                "The predicted outcome/event is not explicitly defined.",
                remediation=(
                    "Define an observable outcome with objective inclusion "
                    "and exclusion criteria."
                ),
            )
        )

    if (
        candidate.prediction_horizon_minutes is None
        or candidate.prediction_horizon_minutes <= 0
    ):
        findings.append(
            _finding(
                FindingCode.HORIZON_UNDEFINED,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.LEAD_TIME,
                "The prediction horizon is undefined or invalid.",
                remediation=(
                    "Declare the prediction horizon and evaluate warning "
                    "lead time against the actual event."
                ),
            )
        )

    required = (
        (
            candidate.false_positive_cost_assessed,
            FindingCode.FALSE_POSITIVE_COST_UNKNOWN,
            ValidationDimension.FALSE_POSITIVES,
            "False-positive consequences have not been assessed.",
            "Quantify alert burden and operational cost of false alarms.",
        ),
        (
            candidate.false_negative_cost_assessed,
            FindingCode.FALSE_NEGATIVE_COST_UNKNOWN,
            ValidationDimension.FALSE_NEGATIVES,
            "False-negative consequences have not been assessed.",
            "Quantify missed-event consequences and asymmetry of error costs.",
        ),
        (
            candidate.lead_time_assessed,
            FindingCode.LEAD_TIME_UNKNOWN,
            ValidationDimension.LEAD_TIME,
            "Actual warning lead time has not been evaluated.",
            "Measure the distribution of warning time before observed outcomes.",
        ),
        (
            candidate.operational_utility_assessed,
            FindingCode.UTILITY_UNASSESSED,
            ValidationDimension.OPERATIONAL_UTILITY,
            "Operational utility has not been evaluated.",
            "Evaluate whether alerts change decisions or improve outcomes.",
        ),
        (
            candidate.human_oversight_implemented,
            FindingCode.HUMAN_OVERSIGHT_MISSING,
            ValidationDimension.HUMAN_OVERSIGHT,
            "Required human oversight is not implemented.",
            "Route operational decisions through an authorized human reviewer.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.automated_operational_action:
        findings.append(
            _finding(
                FindingCode.AUTOMATED_OPERATIONAL_ACTION,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.AUTOMATED_ACTION,
                "The capability can directly trigger an operational action.",
                remediation=(
                    "Separate detection and recommendation from the human "
                    "decision and action layer."
                ),
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 3 — Epidemiology / public health
# ---------------------------------------------------------------------------


def validate_epidemiology(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa validez epidemiológica y sanitaria.

    El gate obliga a diferenciar:

    - casos;
    - tasas;
    - prevalencia;
    - incidencia;
    - flujos;
    - capacidad;
    - ocupación;
    - carga acumulada;
    - y eventos extremos.

    También exige control temporal y de missingness.
    """

    domain = ExpertDomain.EPIDEMIOLOGY_PUBLIC_HEALTH
    findings: list[ValidationFinding] = []

    required = (
        (
            candidate.temporal_validation,
            FindingCode.NO_TEMPORAL_VALIDATION,
            ValidationDimension.TEMPORAL_VALIDITY,
            "Health/system performance has not been temporally validated.",
            "Use temporal holdout evaluation and preserve chronological ordering.",
        ),
        (
            candidate.uncertainty_quantified,
            FindingCode.UNCERTAINTY_MISSING,
            ValidationDimension.UNCERTAINTY,
            "Health risk output lacks quantified uncertainty.",
            "Propagate measurement, sampling and model uncertainty.",
        ),
        (
            candidate.missingness_assessed,
            FindingCode.MISSINGNESS_UNASSESSED,
            ValidationDimension.MISSINGNESS,
            "Missing-data mechanisms have not been assessed.",
            "Evaluate MCAR/MAR/MNAR plausibility and sensitivity to missingness.",
        ),
        (
            candidate.robustness_assessed,
            FindingCode.ROBUSTNESS_UNASSESSED,
            ValidationDimension.ROBUSTNESS,
            "Robustness has not been evaluated.",
            "Test alternative plausible specifications and perturbations.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.validation_dataset is not None:
        if candidate.validation_dataset.positive_events == 0:
            findings.append(
                _finding(
                    FindingCode.INSUFFICIENT_EVIDENCE,
                    FindingSeverity.MAJOR,
                    domain,
                    ValidationDimension.ROBUSTNESS,
                    "The validation dataset contains no positive outcomes.",
                    remediation=(
                        "Obtain an evaluation period containing observed "
                        "events before claiming predictive performance."
                    ),
                )
            )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 4 — Geospatial / border / population
# ---------------------------------------------------------------------------


def validate_geospatial(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa la dimensión espacial.

    El objetivo es impedir que un resultado agregado se interprete como si
    tuviera validez individual o que un modelo espacial se despliegue fuera
    de la escala para la que fue validado.
    """

    domain = ExpertDomain.GEOSPATIAL_POPULATION
    findings: list[ValidationFinding] = []

    result = _missing(
        candidate.spatial_validation,
        code=FindingCode.NO_SPATIAL_VALIDATION,
        severity=FindingSeverity.MAJOR,
        domain=domain,
        dimension=ValidationDimension.SPATIAL_VALIDITY,
        message="Spatial validity has not been demonstrated.",
        remediation=(
            "Validate the model at the spatial resolution and aggregation "
            "level at which it will actually be used."
        ),
    )

    if result is not None:
        findings.append(result)

    if candidate.target_level is TargetLevel.INDIVIDUAL:
        findings.append(
            _finding(
                FindingCode.INVALID_TARGET,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.SPATIAL_VALIDITY,
                "Individual targeting is outside the default system-level "
                "geospatial monitoring scope.",
                remediation=(
                    "Use system/event/population aggregates and apply a "
                    "separate legal and privacy authorization for any "
                    "individual-level processing."
                ),
            )
        )

    if candidate.target_level is TargetLevel.GROUP:
        if candidate.predicts_group_dangerousness:
            findings.append(
                _finding(
                    FindingCode.GROUP_DANGEROUSNESS,
                    FindingSeverity.CRITICAL,
                    domain,
                    ValidationDimension.IDENTITY_INFERENCE,
                    "The capability predicts dangerousness of a group.",
                    remediation=(
                        "Reformulate the target as an observable event, "
                        "system state or environmental condition."
                    ),
                )
            )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 5 — Law / privacy / cybersecurity
# ---------------------------------------------------------------------------


def validate_law_privacy_cybersecurity(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa las barreras de información.

    El gate no sustituye una evaluación jurídica profesional. Comprueba que
    las condiciones técnicas mínimas para una revisión jurídica existan y que
    ciertas arquitecturas intrínsecamente incompatibles con el diseño seguro
    de CeutIA sean bloqueadas.
    """

    domain = ExpertDomain.LAW_PRIVACY_CYBERSECURITY
    findings: list[ValidationFinding] = []

    required = (
        (
            candidate.privacy_reviewed,
            FindingCode.PRIVACY_VIOLATION,
            ValidationDimension.PRIVACY,
            "Privacy review has not been completed.",
            "Document data minimization, purpose limitation, retention and access controls.",
        ),
        (
            candidate.cybersecurity_reviewed,
            FindingCode.SECURITY_VIOLATION,
            ValidationDimension.SECURITY,
            "Cybersecurity review has not been completed.",
            "Review authentication, authorization, secrets, isolation, auditability and attack surface.",
        ),
        (
            candidate.reproducibility_verified,
            FindingCode.REPRODUCIBILITY_MISSING,
            ValidationDimension.REPRODUCIBILITY,
            "Reproducibility has not been verified.",
            "Record versions, parameters, data lineage and execution configuration.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.uses_identity_attributes:
        findings.append(
            _finding(
                FindingCode.IDENTITY_BASED_INFERENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "Identity attributes are used as predictive risk variables.",
                remediation=(
                    "Remove identity-based risk inference and substitute "
                    "validated observable system variables."
                ),
            )
        )

    if candidate.predicts_individual_dangerousness:
        findings.append(
            _finding(
                FindingCode.INDIVIDUAL_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "The capability predicts individual dangerousness.",
                remediation=(
                    "Target observable events or system states instead of "
                    "inherent dangerousness of a person."
                ),
            )
        )

    if candidate.predicts_group_dangerousness:
        findings.append(
            _finding(
                FindingCode.GROUP_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "The capability predicts group dangerousness.",
                remediation=(
                    "Replace group-dangerousness prediction with "
                    "event/system-level monitoring."
                ),
            )
        )

    if candidate.automated_operational_action:
        findings.append(
            _finding(
                FindingCode.AUTOMATED_OPERATIONAL_ACTION,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.AUTOMATED_ACTION,
                "Automated operational action is connected directly to the capability.",
                remediation=(
                    "Require explicit human review and separate the alert "
                    "layer from the action layer."
                ),
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 6 — Statistics / ML / predictive validation
# ---------------------------------------------------------------------------


def validate_statistics_ml(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa la validez estadística y predictiva.

    Especial atención a:

    - calibration;
    - discrimination;
    - temporal/external validation;
    - rare-event behaviour;
    - uncertainty;
    - missingness;
    - drift;
    - subgroup robustness;
    - operational thresholding.
    """

    domain = ExpertDomain.STATISTICS_ML
    findings: list[ValidationFinding] = []

    if candidate.produces_probability and not candidate.calibration_assessed:
        findings.append(
            _finding(
                FindingCode.UNCALIbrATED_PROBABILITY,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.CALIBRATION,
                "A probability is produced without demonstrated calibration.",
                remediation=(
                    "Evaluate calibration-in-the-large, calibration slope "
                    "and reliability on data not used for fitting."
                ),
            )
        )

    if candidate.produces_probability and not candidate.discrimination_assessed:
        findings.append(
            _finding(
                FindingCode.DISCRIMINATION_UNASSESSED,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.DISCRIMINATION,
                "Predictive discrimination has not been evaluated.",
                remediation=(
                    "Evaluate discrimination using metrics appropriate to "
                    "the event prevalence and decision problem."
                ),
            )
        )

    required = (
        (
            candidate.temporal_validation,
            FindingCode.NO_TEMPORAL_VALIDATION,
            ValidationDimension.TEMPORAL_VALIDITY,
            "Temporal validation is missing.",
            "Perform chronological out-of-sample evaluation.",
        ),
        (
            candidate.uncertainty_quantified,
            FindingCode.UNCERTAINTY_MISSING,
            ValidationDimension.UNCERTAINTY,
            "Predictive uncertainty is missing.",
            "Quantify and propagate uncertainty through the prediction pipeline.",
        ),
        (
            candidate.drift_assessed,
            FindingCode.DRIFT_UNASSESSED,
            ValidationDimension.DRIFT,
            "Distribution/model drift has not been assessed.",
            "Monitor covariate, concept and performance drift.",
        ),
        (
            candidate.robustness_assessed,
            FindingCode.ROBUSTNESS_UNASSESSED,
            ValidationDimension.ROBUSTNESS,
            "Robustness has not been assessed.",
            "Run sensitivity and perturbation analyses.",
        ),
        (
            candidate.subgroup_robustness_assessed,
            FindingCode.SUBGROUP_ROBUSTNESS_UNASSESSED,
            ValidationDimension.SUBGROUP_ROBUSTNESS,
            "Subgroup robustness has not been assessed.",
            "Evaluate performance heterogeneity where legally and scientifically appropriate.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    findings.extend(_validate_dataset(candidate, domain))

    if candidate.performance is not None:
        findings.extend(
            _performance_findings(
                candidate.performance,
                domain,
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


def _performance_findings(
    performance: PredictivePerformance,
    domain: ExpertDomain,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []

    for error in performance.validate_ranges():
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.ROBUSTNESS,
                error,
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Cross-domain invariants
# ---------------------------------------------------------------------------


def validate_target_safety(
    candidate: CandidateCapability,
) -> tuple[ValidationFinding, ...]:
    """Aplica restricciones que ningún dominio puede sobrescribir."""

    findings: list[ValidationFinding] = []

    if candidate.predicts_individual_dangerousness:
        findings.append(
            _finding(
                FindingCode.INDIVIDUAL_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                ExpertDomain.LAW_PRIVACY_CYBERSECURITY,
                ValidationDimension.IDENTITY_INFERENCE,
                "Individual dangerousness prediction is prohibited by the "
                "CeutIA system-level monitoring boundary.",
            )
        )

    if candidate.predicts_group_dangerousness:
        findings.append(
            _finding(
                FindingCode.GROUP_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                ExpertDomain.STRATEGIC_INTELLIGENCE,
                ValidationDimension.IDENTITY_INFERENCE,
                "Group dangerousness prediction is prohibited.",
            )
        )

    if candidate.uses_identity_attributes:
        findings.append(
            _finding(
                FindingCode.IDENTITY_BASED_INFERENCE,
                FindingSeverity.CRITICAL,
                ExpertDomain.LAW_PRIVACY_CYBERSECURITY,
                ValidationDimension.IDENTITY_INFERENCE,
                "Identity-based predictive inference is prohibited.",
            )
        )

    if candidate.automated_operational_action:
        findings.append(
            _finding(
                FindingCode.AUTOMATED_OPERATIONAL_ACTION,
                FindingSeverity.CRITICAL,
                ExpertDomain.OPERATIONAL_SECURITY,
                ValidationDimension.AUTOMATED_ACTION,
                "Direct automated operational action is prohibited.",
            )
        )

    return tuple(findings)


def validate_evidence_maturity(
    candidate: CandidateCapability,
) -> tuple[ValidationFinding, ...]:
    """Comprueba que la madurez declarada sea coherente con la evidencia."""

    findings: list[ValidationFinding] = []

    if not candidate.scientific_references:
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.MAJOR,
                ExpertDomain.STATISTICS_ML,
                ValidationDimension.REPRODUCIBILITY,
                "No scientific or methodological references are declared.",
                remediation=(
                    "Attach the scientific/methodological basis for the "
                    "specific metric or model."
                ),
            )
        )

    if candidate.evidence_maturity in {
        EvidenceMaturity.TEMPORALLY_VALIDATED,
        EvidenceMaturity.EXTERNALLY_VALIDATED,
        EvidenceMaturity.PROSPECTIVELY_VALIDATED,
    } and not candidate.temporal_validation:
        findings.append(
            _finding(
                FindingCode.NO_TEMPORAL_VALIDATION,
                FindingSeverity.CRITICAL,
                ExpertDomain.STATISTICS_ML,
                ValidationDimension.TEMPORAL_VALIDITY,
                "Declared evidence maturity exceeds the demonstrated validation.",
            )
        )

    if candidate.evidence_maturity is EvidenceMaturity.EXTERNALLY_VALIDATED:
        dataset = candidate.validation_dataset
        if dataset is None or not dataset.external_dataset:
            findings.append(
                _finding(
                    FindingCode.INSUFFICIENT_EVIDENCE,
                    FindingSeverity.CRITICAL,
                    ExpertDomain.STATISTICS_ML,
                    ValidationDimension.ROBUSTNESS,
                    "External validation is declared without an external dataset.",
                )
            )

    if candidate.evidence_maturity is EvidenceMaturity.PROSPECTIVELY_VALIDATED:
        dataset = candidate.validation_dataset
        if dataset is None or not dataset.prospective_evaluation:
            findings.append(
                _finding(
                    FindingCode.INSUFFICIENT_EVIDENCE,
                    FindingSeverity.CRITICAL,
                    ExpertDomain.STATISTICS_ML,
                    ValidationDimension.TEMPORAL_VALIDITY,
                    "Prospective validation is declared without prospective evaluation.",
                )
            )

    return tuple(findings)


# ---------------------------------------------------------------------------
# Global adversarial validator
# ---------------------------------------------------------------------------


EXPERT_GATES: Final[tuple[ExpertDomain, ...]] = (
    ExpertDomain.STRATEGIC_INTELLIGENCE,
    ExpertDomain.OPERATIONAL_SECURITY,
    ExpertDomain.EPIDEMIOLOGY_PUBLIC_HEALTH,
    ExpertDomain.GEOSPATIAL_POPULATION,
    ExpertDomain.LAW_PRIVACY_CYBERSECURITY,
    ExpertDomain.STATISTICS_ML,
)


def run_adversarial_validation(
    candidate: CandidateCapability,
    *,
    now: datetime | None = None,
) -> AdversarialValidationReport:
    """
    Ejecuta los seis gates y determina elegibilidad operacional.

    Regla de decisión:

    CRITICAL
        => BLOCK

    MAJOR unresolved
        => SHADOW_ONLY

    Sin MAJOR/CRITICAL
        => PASS

    Los hallazgos INFO/MINOR no bloquean por sí mismos.

    El resultado es deliberadamente fail-closed.
    """

    timestamp = now or datetime.now().astimezone()

    expert_results = (
        validate_strategic_intelligence(candidate),
        validate_operational_security(candidate),
        validate_epidemiology(candidate),
        validate_geospatial(candidate),
        validate_law_privacy_cybersecurity(candidate),
        validate_statistics_ml(candidate),
    )

    cross_domain_findings = (
        *validate_target_safety(candidate),
        *validate_evidence_maturity(candidate),
    )

    all_findings = tuple(
        finding
        for result in expert_results
        for finding in result.findings
    ) + tuple(cross_domain_findings)

    critical = tuple(
        finding.code
        for finding in all_findings
        if finding.severity is FindingSeverity.CRITICAL
    )

    major = tuple(
        finding.code
        for finding in all_findings
        if finding.severity is FindingSeverity.MAJOR
    )

    if critical:
        decision = ValidationDecision.BLOCK
    elif major:
        decision = ValidationDecision.SHADOW_ONLY
    else:
        decision = ValidationDecision.PASS

    return AdversarialValidationReport(
        capability_id=candidate.capability_id,
        decision=decision,
        generated_at=timestamp,
        expert_results=expert_results,
        findings=all_findings,
        mandatory_failures=critical,
        unresolved_major_failures=major,
    )


def assert_operationally_eligible(
    report: AdversarialValidationReport,
) -> None:
    """
    Impide que una capacidad no aprobada continúe hacia producción.

    Raises
    ------
    RuntimeError
        Si el resultado es BLOCK o SHADOW_ONLY.
    """

    if report.decision is ValidationDecision.PASS:
        return

    if report.decision is ValidationDecision.BLOCK:
        raise RuntimeError(
            "CeutIA adversarial validation BLOCKED capability "
            f"{report.capability_id}: "
            f"{len(report.mandatory_failures)} critical finding(s)."
        )

    raise RuntimeError(
        "CeutIA capability "
        f"{report.capability_id} is SHADOW_ONLY and cannot be used "
        "for operational decisions."
    )


# ---------------------------------------------------------------------------
# Deterministic summary for APIs / audit
# ---------------------------------------------------------------------------


def summarize_report(
    report: AdversarialValidationReport,
) -> dict[str, object]:
    """
    Genera una representación serializable y segura del resultado.

    No incluye datos personales, fuentes privadas ni contenido operacional.
    """

    by_domain: dict[str, dict[str, int]] = {}

    for result in report.expert_results:
        by_domain[result.domain.value] = {
            "findings": len(result.findings),
            "major": result.major_count,
            "critical": result.critical_count,
            "passed": int(result.passed),
        }

    severity_counts = {
        severity.value: sum(
            finding.severity is severity
            for finding in report.findings
        )
        for severity in FindingSeverity
    }

    return {
        "capability_id": report.capability_id,
        "decision": report.decision.value,
        "generated_at": report.generated_at.isoformat(),
        "severity_counts": severity_counts,
        "domains": by_domain,
        "mandatory_failures": tuple(
            code.value for code in report.mandatory_failures
        ),
        "unresolved_major_failures": tuple(
            code.value for code in report.unresolved_major_failures
        ),
    }


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------


SCIENTIFIC_INVARIANTS: Final[tuple[str, ...]] = (
    "A mathematically valid formula is not automatically operationally valid.",
    "A published model is not automatically validated for CeutIA.",
    "Retrospective fit is not prospective validation.",
    "Discrimination is not calibration.",
    "Calibration is not causal validity.",
    "Prediction is not explanation.",
    "Correlation is not causation.",
    "Source count is not source independence.",
    "Viral content is evidence that content exists, not evidence that its claim is true.",
    "Contradictory evidence must remain representable.",
    "Unknown must remain distinguishable from zero.",
    "Missing data must not silently become risk.",
    "Probability requires calibration evidence.",
    "Rare-event prediction requires explicit evaluation of class imbalance and calibration.",
    "Spatial aggregation does not justify individual inference.",
    "Population-level association does not justify individual-level prediction.",
    "Nationality or origin must not be used as a proxy for dangerousness.",
    "Group identity must not become a dangerousness score.",
    "CeutIA detects system/event signals; authorized humans interpret operational consequences.",
    "An alert is not an instruction to act.",
    "An operational decision must not be generated solely by an automated alert.",
    "Every production capability must have an auditable validation history.",
    "Every prediction must be retrospectively comparable with an observed outcome.",
    "Every model must have an explicit failure boundary.",
    "Every public output must be independently authorized by the information boundary.",
)


def validate_invariants() -> tuple[str, ...]:
    """
    Validación estática de las invariantes fundamentales.

    Returns an empty tuple when the invariant registry is structurally valid.
    """

    errors: list[str] = []

    if len(SCIENTIFIC_INVARIANTS) != len(set(SCIENTIFIC_INVARIANTS)):
        errors.append("Duplicate scientific invariant detected.")

    if len(EXPERT_GATES) != len(set(EXPERT_GATES)):
        errors.append("Duplicate expert gate detected.")

    if set(EXPERT_GATES) != set(ExpertDomain):
        errors.append(
            "The adversarial validator must cover exactly all six expert domains."
        )

    return tuple(errors)


_INVARIANT_ERRORS = validate_invariants()

if _INVARIANT_ERRORS:
    raise RuntimeError(
        "CeutIA adversarial validation invariant failure: "
        + "; ".join(_INVARIANT_ERRORS)
    )


__all__ = [
    "AdversarialValidationReport",
    "CandidateCapability",
    "DataUseMode",
    "EvidenceMaturity",
    "ExpertDomain",
    "ExpertGateResult",
    "FindingCode",
    "FindingSeverity",
    "PredictivePerformance",
    "SCIENTIFIC_INVARIANTS",
    "TargetLevel",
    "ValidationDataset",
    "ValidationDecision",
    "ValidationDimension",
    "ValidationFinding",
    "assert_operationally_eligible",
    "run_adversarial_validation",
    "summarize_report",
    "validate_epidemiology",
    "validate_geospatial",
    "validate_invariants",
    "validate_law_privacy_cybersecurity",
    "validate_operational_security",
    "validate_statistics_ml",
    "validate_strategic_intelligence",
    "validate_target_safety",
]