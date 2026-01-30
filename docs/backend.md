# Backend

The backend is a FastAPI app with async SQLAlchemy and Alembic migrations.

## Tech stack

- FastAPI
- Pydantic v2
- SQLAlchemy 2 (async)
- asyncpg
- Alembic
- web3.py + eth-account (HD derivation, chain reads, optional sends)

## App layout

- `app/main.py` — FastAPI app + CORS + router mounting
- `app/core/config.py` — settings (dotenv + pydantic-settings)
- `app/api/v1/api.py` — API router with prefixes
- `app/api/v1/endpoints/` — route modules
- `app/models/` — SQLAlchemy models
- `app/services/` — operational services (wallet derivation, access control, entity gate)
- `app/entities/` — entity runtime + arena compiler

## Database models

- `User` — user record with `derivation_index`
- `Wallet` — chain-tagged address rows per user (ethereum/bsc/polygon)
- `Transaction` — internal ledger events (DEPOSIT/WITHDRAWAL) with `tx_hash`
- `Agreement` — off-chain agreement records (DB)
- `HearingRecordModel` — persisted entity hearing records (JSONB)

## API routers

Mounted under `/api/v1`:

- `/users` — create/get-or-create user + derived wallets
- `/wallets` — read balances for custodial wallets
- `/transactions` — withdrawals + history (internal ledger)
- `/agreements` — DB agreements + token gate check
- `/hearing` — entity pipeline endpoints + persistence + gate endpoint

See [API Reference](api.md) for endpoint details.

## Entity runtime (important)

The backend implements a pure-function entity pipeline:

Perception → Memory → Risk → Strategy → Execution

Orchestrated by the Arena Compiler:

- `app/entities/arena.py` → `compile_hearing()`

This produces a typed `HearingRecord` defined in:

- `app/schemas/hearing.py`

## Configuration

Settings are loaded in `app/core/config.py`.

Common variables:

- `DATABASE_URL`
- `BACKEND_CORS_ORIGINS`
- `CITADEL_MASTER_SEED`
- `ETHEREUM_RPC_URL`, `BSC_RPC_URL`, `POLYGON_RPC_URL`

Note: some modules also read additional env vars directly (example: `USE_MAINNET` in `app/services/access_control.py`).

## Migrations

- Alembic lives in `backend/alembic/`.
- Run: `alembic upgrade head`

The hearing record persistence uses a `hearing_records` table with a JSONB payload.
