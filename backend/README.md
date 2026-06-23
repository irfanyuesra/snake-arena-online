# Snake Arena Online — Backend

FastAPI implementation of `openapi.yaml`. Uses an in-memory store (no database
yet), seeded with fake users, scores, and active games. Authenticated endpoints
use bearer tokens; passwords are hashed with PBKDF2 (standard library only).

## Layout

```
backend/
  app/
    main.py        # FastAPI app, error shape, CORS, router wiring
    models.py      # Pydantic models mirroring the OpenAPI schemas
    auth.py        # password hashing + bearer-token dependencies
    store.py       # in-memory store and seed data
    events.py      # pub/sub broker for the SSE streams
    routers/       # auth, leaderboard, games
  tests/           # pytest suite
  requirements.txt
```

All routes are served under the `/api` prefix (matching the spec's server URL).

## Setup

```bash
cd backend
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

- API:        http://localhost:8000/api
- Swagger UI:  http://localhost:8000/docs
- Health:      http://localhost:8000/health

## Seed accounts

| username | password |
|----------|----------|
| demo     | demo     |
| alice    | alice    |
| bob      | bob      |

## Tests

```bash
cd backend
pytest
```
