# App Overview

Citadel is a wallet + escrow prototype with an additional institutional “control plane”: a set of non-collaborating entities that cross-examine each other and can **block actions** under uncertainty.

## What the user experiences

### 1) Identity bootstrap (custodial)

- The landing page (`/`) creates or retrieves a user via email.
- The backend derives a deterministic EVM address from a server-side master mnemonic and returns **custodial deposit addresses** for:
  - Ethereum
  - BSC
  - Polygon

This is represented as “Custodial Identity System” in the UI.

### 2) Dashboard

The dashboard (`/dashboard`) is the primary hub and merges two worlds:

- **Custodial view** (server-derived addresses): shows balances fetched from backend `/wallets/{user_id}/balances`.
- **On-chain view** (MetaMask): connects a single MetaMask account and shows live BNB + TST balance on the active BSC network.

### 3) On-chain escrow

The escrow page (`/agreements`) uses MetaMask + ethers to interact directly with the on-chain escrow contract:

- Approve TST spending
- Create and fund an escrow agreement
- Release funds (payer-only)

### 4) Hearing transcript

The hearing page (`/hearing`) renders a calm, readable transcript of the entity pipeline.

Initially it loads `/api/v1/hearing/example` (read-only), but the backend also supports running and persisting real hearing records.

## What makes this repo unusual

Most wallet apps are “UI + web3 calls”. This repo adds:

- A strict, typed “hearing record” contract
- An entity pipeline: Perception → Memory → Risk → Strategy → Execution
- A gate endpoint that returns `allowed/reason/hearing` so the UI can block actions with an explanation

This creates a system that is designed to be:

- **Audit-friendly**: every decision can be explained and stored.
- **Constraint-first**: the Risk entity has absolute veto power.
- **Anti-blob**: entities are separated by mandate.

## Product direction note

The codebase currently includes both:

- Custodial identity + derived deposit addresses (backend)
- MetaMask self-custody for on-chain actions (frontend)

This can be a deliberate hybrid, but it should be documented and reconciled in product decisions (see Wallet System docs).
