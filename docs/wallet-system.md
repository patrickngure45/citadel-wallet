# Wallet System

This repo currently contains **two wallet concepts**:

1) **Custodial derived wallets (backend)** — deposit addresses derived from a server-side master seed.
2) **MetaMask self-custody (frontend)** — one active wallet account used for on-chain actions.

Both are valid patterns, but they must be clearly understood and intentionally chosen.

## 1) Custodial derived wallets (backend)

### What it is

- When a user is created (`POST /api/v1/users/`), the backend allocates a `derivation_index`.
- It derives an EVM address from `CITADEL_MASTER_SEED` using BIP44 path:

  `m/44'/60'/0'/0/{index}`

- The same derived address is stored for three chain rows: `ethereum`, `bsc`, `polygon`.

### What it enables

- Users can deposit to addresses shown in `/` without connecting MetaMask.
- Backend can monitor balances via RPC reads.
- Backend can implement “internal ledger” withdrawals (funds sent from a master/hot wallet).

### Current limitations (important)

- `GET /wallets/{user_id}/balances` currently reads **native coin only** (ETH/BNB/MATIC). ERC20 balances are separate.
- Custodial addresses are derived server-side: this is **custody**. You must treat the seed as production-grade secret material.

## 2) MetaMask wallet (frontend) — single wallet model

### What it is

- The UI connects to `window.ethereum` (MetaMask) via ethers v6.
- The “active wallet” is always the currently selected MetaMask account (`accounts[0]`).

### What it enables

- On-chain TST transfers
- On-chain escrow interactions (approve + create/fund + release)

### Single wallet policy

The app should operate as “one MetaMask wallet at a time”:

- Every on-chain action is executed by the current MetaMask signer.
- If the user changes accounts, the UI state follows the new active account.

If you want stricter behavior (example: bind a user identity to exactly one MetaMask address), add an explicit link step:

- user signs a message
- backend stores the verified MetaMask address
- UI refuses to operate if account != bound address

## 3) Important reconciliation: custodial identity vs MetaMask

Today:

- `/` creates a custodial identity and shows deposit addresses (server-derived).
- `/dashboard` also supports MetaMask and on-chain operations.

This is a hybrid. Decide which is “the product truth”:

- **MetaMask-first product** (self-custody): backend should not derive user deposit keys; instead store the user’s MetaMask address and treat it as canonical.
- **Custodial-first product**: MetaMask should be removed or downgraded; actions should be queued/executed by backend with full compliance and security posture.

If the requirement is “we use only one MetaMask wallet,” then the docs and UI should treat MetaMask as the canonical user wallet, and custodial derivation becomes admin-only (or removed).

## 4) Network toggles

- Frontend: `NEXT_PUBLIC_USE_MAINNET` controls BSC mainnet/testnet.
- Backend (access control module): `USE_MAINNET` controls which TST contract is checked.

If you want predictable behavior, unify these toggles (one variable name, one source of truth).
