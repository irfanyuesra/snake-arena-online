# syntax=docker/dockerfile:1

# 1) Python dependencies via uv -> /app/.venv
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# Use the image's system Python so the venv we copy into the final stage
# points at an interpreter that exists there too.
ENV UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Frontend build -> static SPA in /frontend/dist/client
FROM node:22-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
# npm install (not ci): the lockfile is generated on Windows and lists
# platform-specific optional deps that `npm ci` rejects strictly; install
# resolves the right binaries for this platform instead.
RUN npm install --no-audit --no-fund
COPY frontend .
RUN npm run build

# 3) Runtime: Python serves the API and the compiled frontend on one port
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY backend/app ./app
COPY --from=frontend-builder /frontend/dist/client ./static
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
