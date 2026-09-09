"""API PUBLIC mínima: respuesta estratificada. Sin scores de riesgo."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="CeutIA PUBLIC", version="0.0.1-non-operational")


class CitizenQuery(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class StratifiedAnswer(BaseModel):
    layer: str  # hecho | hipotesis | no_verificado
    content: str
    sources: list[str]
    limitations: list[str]


@app.post("/public/query", response_model=StratifiedAnswer)
def public_query(q: CitizenQuery) -> StratifiedAnswer:
    # Sin datos reales conectados: respuesta honesta
    return StratifiedAnswer(
        layer="no_verificado",
        content=(
            "CeutIA no tiene en este momento un pipeline de evidencia "
            "conectado a fuentes oficiales de Ceuta para responder con veracidad demostrada."
        ),
        sources=[],
        limitations=[
            "Sin feeds oficiales ingestados",
            "Sin calibración de riesgo",
            "Sin comprobación de independencia de fuentes en runtime",
            "No dirigir discurso ni emitir alertas automáticas",
        ],
    )