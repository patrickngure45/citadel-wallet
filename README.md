# Citadel Wallet & Control Plane

Citadel is a hybrid **non-custodial / custodial** wallet prototype featuring an institutional "Control Plane". Unlike standard wallets, Citadel employs a set of non-collaborating AI entities that cross-examine every high-value transaction before execution.

## 🚀 Live Deployment

- **Frontend**: [https://citadel-wallet.vercel.app](https://citadel-wallet.vercel.app)
- **Backend API**: [https://citadel-backend-pxu0.onrender.com](https://citadel-backend-pxu0.onrender.com)
- **Network**: BSC Mainnet (Chain ID: 56)

## 🏗 Architecture

### Frontend (Next.js 16)
- **Framework**: Next.js 16 (App Router)
- **Hosting**: Vercel
- **Web3**: ethers.js + MetaMask
- **Key Features**:
  - `Agreements`: On-chain escrow interface.
  - `Dashboard`: Unified view of custodial (derived) and non-custodial (MetaMask) assets.
  - `Hearing`: Visual interface for the AI Control Plane decisions.

### Backend (FastAPI)
- **Framework**: FastAPI
- **Hosting**: Render
- **Database**: NeonDB (PostgreSQL + AsyncPG)
- **AI Engine**:
  - **Perception**: Fetches real-time data (Binance API, On-chain).
  - **Memory**: Stores historical context (Postgres).
  - **Risk**: Evaluates transaction safety (Logic + Heuristics).
  - **Strategy**: Optimizes execution parameters.
  - **Execution**: Signs and broadcasts transactions (or generates calldata).

## 🔧 Environment Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker (optional)

### Backend Setup
1. `cd backend`
2. `pip install -r requirements.txt`
3. Configure `.env` (see `.env.example`)
4. Run locally: `uvicorn app.main:app --reload`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. Run locally: `npm run dev`

## 🔐 Smart Contracts (BSC Mainnet)

| Contract | Address | Status |
|----------|---------|--------|
| **TST Token** | `0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71` | Active |
| **Citadel Escrow** | `0xEd6C769f17d6462A5DB87395a9Ae30A274afAE49` | Active |
| **TST Escrow** | `0x922bA3bD7866F92F0Caa2A544bb303A38922fb12` | Active |

## 🛡️ The "Hearing" Protocol

Every critical action triggers a "Hearing":
1. **Perception** gathers facts (Gas price, Token liquidity, User history).
2. **Memory** recalls similar past events.
3. **Risk** debates safety (halts if risk > threshold).
4. **Strategy** plans the route.
5. **Execution** finalizes the action.
