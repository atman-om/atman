FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /workspace/
COPY services /workspace/services
COPY packages /workspace/packages
COPY alembic.ini /workspace/alembic.ini
COPY migrations /workspace/migrations
COPY datasets /workspace/datasets
COPY prompts /workspace/prompts

RUN pip install --upgrade pip && pip install -e ".[dev]"

EXPOSE 8000
CMD ["sh", "-c", "uvicorn services.api.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
