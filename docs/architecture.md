# Architecture

This repo is a full-stack prototype:

- `frontend/` — Next.js App Router UI
- `backend/` — FastAPI API + entity runtime + Postgres persistence
- `contracts/` — Solidity contracts (token + escrow)

## High-level data flows

### A) Custodial identity flow (server-derived)

1. User enters email on `/`
2. Frontend calls `POST /api/v1/users/`
3. Backend:
   - allocates a derivation index
   - derives an EVM address from `CITADEL_MASTER_SEED`
   - stores it in DB as 3 chain-specific wallet rows (ethereum/bsc/polygon)
4. Frontend stores `citadel_user_id` in `localStorage`

### B) Custodial balances flow

1. Dashboard calls `GET /api/v1/wallets/{user_id}/balances`
2. Backend reads native balances from chain RPCs via `web3.py`

### C) MetaMask on-chain flow (single active wallet)

1. User connects MetaMask via `window.ethereum`
2. Frontend:
   - checks network (BSC testnet/mainnet)
   - reads BNB balance via RPC
   - reads TST balance via ERC20 `balanceOf`
3. For writes, frontend uses ethers v6 `BrowserProvider` signer:
   - `transfer()` for token transfers
   - escrow `approve()` then `createAndFund()`

### D) Entity gate + hearing record flow

1. UI or service calls `POST /api/v1/hearing/gate`
2. Backend runs:
   - Perception → Memory → Risk → Strategy → Execution
3. Returns:
   - `allowed: boolean`
   - `reason: string`
   - `hearing: HearingRecord`
4. Optionally persists the record into `hearing_records` (JSONB)

## Folder structure (important parts)

### Frontend

- `frontend/src/app/`
  - `page.tsx` — identity bootstrap + displays custodial deposit addresses
  - `dashboard/page.tsx` — portfolio hub + MetaMask connect + transfer
  - `agreements/page.tsx` — on-chain escrow UI
  - `hearing/page.tsx` — transcript UI
- `frontend/src/components/WalletConnect.tsx` — connect button + status + balances
- `frontend/src/hooks/useWeb3.ts` — wallet state + balance refresh
- `frontend/src/lib/`
  - `contracts.ts` — network toggle + contract addresses + ABIs
  - `web3.ts` — ethers helpers (read + write)
  - `hearing.ts` — TS types for hearing record (if present)

### Backend

- `backend/app/main.py` — FastAPI app + CORS + router
- `backend/app/api/v1/` — API routers
- `backend/app/models/` — SQLAlchemy models (`User`, `Wallet`, `Agreement`, `Transaction`, `HearingRecordModel`)
- `backend/app/services/`
  - `wallet_service.py` — HD derivation + chain RPC helpers + transfer helpers
  - `access_control.py` — token-gated access checks (phase-0 bypass exists)
  - `entity_gate.py` — turns entity pipeline into a gating service
- `backend/app/entities/` — entity runtime modules + arena compiler
- `backend/alembic/` — migrations

## Design system

- Next.js uses `next/font/google` for **Geist Sans** + **Geist Mono**.
- Styling uses Tailwind v4 and custom CSS variables:
  - `--background: #0b0d14`
  - `--foreground: #e0e7ff`
  - `--card: #151923`
  - `--primary: #6366f1`

The current visual theme is cohesive and should be treated as a stable base.
