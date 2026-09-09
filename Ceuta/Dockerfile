# ============================================================
# CeutIA — Production Python Runtime
# ============================================================

# Python version explicitly constrained by pyproject.toml.
FROM python:3.12-slim

# ------------------------------------------------------------
# Runtime environment
# ------------------------------------------------------------

# Prevent Python from creating .pyc files inside the container.
ENV PYTHONDONTWRITEBYTECODE=1

# Send Python stdout/stderr directly to the container logs.
ENV PYTHONUNBUFFERED=1

# The Python package root defined by pyproject.toml is /app/backend.
ENV PYTHONPATH=/app/backend

# ------------------------------------------------------------
# Application directory
# ------------------------------------------------------------

WORKDIR /app

# ------------------------------------------------------------
# Non-root runtime user
# ------------------------------------------------------------

# CeutIA must not run the application as root.
RUN groupadd --system ceutia \
    && useradd \
        --system \
        --gid ceutia \
        --home-dir /app \
        --no-create-home \
        --shell /usr/sbin/nologin \
        ceutia

# ------------------------------------------------------------
# Python project metadata
# ------------------------------------------------------------

# Copy the packaging metadata first so dependency installation
# is separated from the application source layer.
COPY pyproject.toml README.md ./

# ------------------------------------------------------------
# Application source
# ------------------------------------------------------------

# pyproject.toml declares:
# package-dir = { "" = "backend" }
# therefore the backend package must exist at /app/backend.
COPY backend ./backend

# ------------------------------------------------------------
# Python dependencies
# ------------------------------------------------------------

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

# ------------------------------------------------------------
# File ownership
# ------------------------------------------------------------

RUN chown -R ceutia:ceutia /app

# ------------------------------------------------------------
# Runtime privilege
# ------------------------------------------------------------

USER ceutia

# ------------------------------------------------------------
# API port
# ------------------------------------------------------------

EXPOSE 8000

# ------------------------------------------------------------
# Application entrypoint
# ------------------------------------------------------------

# pyproject.toml defines the application package under backend/.
# The FastAPI application will be exposed as app.main:app.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]