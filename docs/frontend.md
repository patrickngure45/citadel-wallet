# Frontend

The UI is a Next.js App Router application.

## Tech stack

- Next.js 16 (App Router)
- React 19
- Tailwind CSS v4
- Framer Motion (micro-interactions)
- Lucide icons
- ethers v6 (MetaMask + contract calls)

## Design, theme, and fonts

- Fonts are loaded via `next/font/google`:
  - Geist Sans (`--font-geist-sans`)
  - Geist Mono (`--font-geist-mono`)
- Global theme variables live in `src/app/globals.css`.
- The UI uses a dark, glassy aesthetic (blurred panels, subtle borders) with:
  - **indigo** as the primary accent
  - **amber/orange** for token emphasis

Design quality note: the current UI is already polished and coherent. Future feature work should preserve spacing, typography, and the calm “control room” feel.

## Pages

### `/` — Identity bootstrap

File: `src/app/page.tsx`

- Creates a user by calling `POST {NEXT_PUBLIC_API_URL}/users/`.
- Stores the returned `id` in `localStorage` as `citadel_user_id`.
- Displays server-derived deposit addresses (custodial identity).

### `/dashboard` — Portfolio hub

File: `src/app/dashboard/page.tsx`

- Fetches custodial balances from `GET /wallets/{user_id}/balances`.
- Shows a MetaMask connect control (single active wallet) via `WalletConnect`.
- Displays on-chain BNB + TST balances when connected.
- Supports TST transfers directly from MetaMask.

Note: total net worth uses mock prices for ETH/BNB/MATIC (demo scaffolding).

### `/agreements` — On-chain escrow

File: `src/app/agreements/page.tsx`

- Requires MetaMask connection.
- Uses escrow contract via ethers:
  - `approve()` TST spending
  - `createAndFund()` agreement
  - `releaseFunds()` for payer

### `/hearing` — Hearing transcript

File: `src/app/hearing/page.tsx`

- Fetches an example hearing record from `GET /hearing/example`.
- Renders typed entity outputs and `arena_findings`.

## Web3 modules

### Network toggle

`src/lib/contracts.ts`

- Controlled by `NEXT_PUBLIC_USE_MAINNET`:
  - `false` → BSC testnet (chainId 97)
  - `true` → BSC mainnet (chainId 56)

### Wallet model: single MetaMask wallet

The app uses one active wallet at a time:

- The “active wallet” is `window.ethereum`’s selected account (`accounts[0]`).
- Account switching is supported, but UI state always binds to the currently selected account.

If you want to hard-enforce *one account only* (disallow switching), implement that policy at the UI layer.

## Environment variables

- `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000/api/v1`)
- `NEXT_PUBLIC_USE_MAINNET` (`true`/`false`)
