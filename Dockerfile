FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 8000

CMD uv run alembic upgrade head && \
    exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 \
    --no-access-log --proxy-headers --forwarded-allow-ips='*'