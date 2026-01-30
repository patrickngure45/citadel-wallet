# Quickstart (Local Development)

## Prerequisites

- Node.js (recommended: current LTS)
- Python 3.10+
- Postgres 15 (or Docker)

## Environment variables

This repo uses environment variables for DB and chain RPC access.

- Backend reads from `backend/.env` **and** the repo root `.env` (see `backend/app/core/config.py`).
- Frontend reads `NEXT_PUBLIC_*` variables at build/runtime.

Create a local `.env` **outside of git** and populate values (examples only):

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/citadel
SECRET_KEY=change-me
CITADEL_MASTER_SEED="twelve words ..."
ETHEREUM_RPC_URL=https://...
BSC_RPC_URL=https://...
POLYGON_RPC_URL=https://...
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_USE_MAINNET=false
```

## Run with Docker (DB + backend)

From repo root:

```bash
docker compose up --build
```

This starts:

- Postgres on `localhost:5432`
- Backend on `http://localhost:8000`

## Run backend (venv)

From repo root:

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Run frontend

From repo root:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`.

## Sanity checks

- Backend OpenAPI: `http://localhost:8000/api/v1/openapi.json`
- Hearing example: `http://localhost:8000/api/v1/hearing/example`
- App: `http://localhost:3000`

## Notes

- The frontend is configured to use BSC testnet by default via `NEXT_PUBLIC_USE_MAINNET=false`.
- The backend has a separate toggle used by `app/services/access_control.py`: `USE_MAINNET` (not `NEXT_PUBLIC_USE_MAINNET`).
  - If you want them consistent, unify these env names in code.
