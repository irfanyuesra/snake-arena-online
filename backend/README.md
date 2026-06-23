# Snake Arena Online — Backend

FastAPI implementation of `openapi.yaml`. Uses an in-memory store (no database
yet), seeded with fake users, scores, and active games. Authenticated endpoints
use **JWT bearer tokens**; passwords are hashed with PBKDF2 (standard library).

Managed with [uv](https://docs.astral.sh/uv/).

## Layout

```
backend/
  app/
    main.py        # FastAPI app, CORS, mounts routers under /api, docs at /api/docs
    models.py      # Pydantic request/response models
    auth.py        # password hashing + JWT bearer tokens
    store.py       # in-memory store and seed data
    events.py      # pub/sub broker for the SSE streams
    routers/       # auth.py, leaderboard.py, games.py
  tests/           # one test file per router
  pyproject.toml
```

All routes are served under the `/api` prefix (matching the spec's server URL).

## Setup

```bash
cd backend
uv sync
```

## Run

```bash
uv run uvicorn app.main:app --reload --port 8000
```

- API:        http://localhost:8000/api
- Swagger UI:  http://localhost:8000/api/docs
- OpenAPI:     http://localhost:8000/api/openapi.json
- Health:      http://localhost:8000/health

The live docs are generated from the actual routes — compare them against the
project's `openapi.yaml` to confirm the backend matches the agreed API.

## Database

Persistence uses SQLAlchemy and is configured entirely by the `DATABASE_URL`
environment variable, so the same code runs on SQLite or Postgres:

```bash
# SQLite (single file, zero setup)
DATABASE_URL=sqlite:///./snake.db

# Postgres
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/snake_arena
```

Set it in `backend/.env` (gitignored). Tables are created and seed data is
inserted on first startup. `*.db` files are local state and are gitignored.

## Auth

JWTs are signed with HS256. Set `SNAKE_JWT_SECRET` in production; in dev a
random per-process secret is used (tokens reset when the server restarts).
Logout adds the token's `jti` to an in-memory deny-list so it stops working.

## Seed accounts

| username | password |
|----------|----------|
| demo     | demo     |
| alice    | alice    |
| bob      | bob      |

## Tests

```bash
cd backend
uv run pytest                  # fast unit tests (in-memory SQLite)
uv run pytest tests_integration/   # integration tests (on-disk SQLite)
```

Or via the Makefile from the repo root: `make backend-tests` and
`make test-integration`.
