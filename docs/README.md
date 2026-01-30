# Citadel Wallet — Documentation Index

This repository is a full-stack wallet + escrow prototype with an additional **entity-based “control plane”** (cross-examination pipeline) that can gate actions and produce a calm, auditable transcript (“hearing record”).

## What exists today (truthful snapshot)

- **Frontend**: Next.js App Router (React 19) + Tailwind v4 + Framer Motion + Lucide icons
- **Backend**: FastAPI + Pydantic v2 + async SQLAlchemy + Alembic
- **DB**: Postgres (JSONB used for hearing record persistence)
- **On-chain (frontend)**: MetaMask via `window.ethereum` + ethers v6, BSC mainnet/testnet toggle, TST token, on-chain escrow contract
- **Custodial identity (backend)**: HD-wallet derived deposit addresses per user (from `CITADEL_MASTER_SEED`) for Ethereum/BSC/Polygon

> Design note: the UI is already very strong and consistent (dark/glass aesthetic, indigo + amber accents, Geist fonts). Treat the visual system as “locked” unless intentionally redesigning.

## Docs

- [Quickstart](quickstart.md)
- [App Overview](app-overview.md)
- [Architecture](architecture.md)
- [Frontend](frontend.md)
- [Backend](backend.md)
- [Wallet System](wallet-system.md)
- [Entities (Cross‑Examination)](entities.md)
- [API Reference](api.md)
- [Security & Secrets](security.md)

## Terms

- **Custodial identity**: user record + deposit addresses derived from a server-side master seed.
- **MetaMask wallet**: the single active browser wallet (the user’s selected account) used for on-chain actions from the UI.
- **Hearing record**: a typed envelope that contains entity outputs and arena findings.
