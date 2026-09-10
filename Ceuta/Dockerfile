# ============================================================
# CeutIA — Production Python Runtime
# ============================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

RUN groupadd --system ceutia \
    && useradd \
        --system \
        --gid ceutia \
        --home-dir /app \
        --no-create-home \
        --shell /usr/sbin/nologin \
        ceutia

# Keep packaging metadata in its own layer.
COPY pyproject.toml README.md ./

# Canonical backend package.
COPY backend ./backend

# Continuous monitor used by docker-compose.
COPY ceuta-final ./ceuta-final

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir . \
    && chown -R ceutia:ceutia /app

USER ceutia

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
