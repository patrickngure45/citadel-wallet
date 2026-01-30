# Citadel: Repository Structure & Setup Guide

**For:** Next AI session to set up the project properly  
**Brand:** Citadel | **Protocol:** TradeSynapse

---

## TARGET DIRECTORY STRUCTURE (After Phase 0 completion)

```
wallet-trial/
├── docs/
│   ├── PROJECT_MANIFEST.md ✅ (DONE)
│   ├── IMPLEMENTATION_ROADMAP.md ✅ (DONE)
│   ├── PROGRESS_TRACKER.md ✅ (DONE)
│   ├── QUICK_REFERENCE.md ✅ (DONE)
│   ├── ARCHITECTURE.md (Week 2)
│   ├── DATABASE_SCHEMA.md (Week 2) ← NEXT
│   ├── API_CONTRACTS.md (Week 2) ← NEXT
│   ├── SMART_CONTRACTS.md (Week 2) ← NEXT
│   ├── FRONTEND_ROUTES.md (Week 2)
│   ├── ENTITY_COMMUNICATION.md (Week 2)
│   ├── SECURITY_CHECKLIST.md (Week 2)
│   ├── TESTING_STRATEGY.md (Week 2)
│   ├── DEPLOYMENT.md (Week 2)
│   └── MONITORING.md (Week 2)
│
├── backend/
│   ├── requirements.txt (list all dependencies)
│   ├── .env.example (template)
│   ├── app.py (main FastAPI entry point, later refactored)
│   ├── config/
│   │   └── settings.py (environment variables, config)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── perception_service.py (Fly.io service 1)
│   │   ├── memory_service.py (Fly.io service 2)
│   │   ├── risk_service.py (Fly.io service 3)
│   │   ├── strategy_service.py (Fly.io service 4)
│   │   ├── execution_service.py (Fly.io service 5)
│   │   ├── signing_service.py (Isolated, HSM protected)
│   │   ├── wallet_service.py (HD derivation, BIP44)
│   │   ├── guardian_service.py (Anomaly detection, 2FA)
│   │   ├── audit_service.py (IPFS logging)
│   │   └── token_service.py (TST token interactions)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── wallet_routes.py (wallet endpoints)
│   │   ├── entity_routes.py (entity status endpoints)
│   │   ├── execution_routes.py (execution history)
│   │   ├── guardian_routes.py (anomaly checks + 2FA)
│   │   ├── audit_routes.py (export + IPFS)
│   │   ├── token_routes.py (staking + claims)
│   │   └── health_routes.py (service health checks)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_models.py (Pydantic: User, Profile)
│   │   ├── wallet_models.py (Pydantic: Wallet, Balance)
│   │   ├── decision_models.py (Pydantic: Decision, EntityLog)
│   │   ├── guardian_models.py (Pydantic: AnomalyCheck)
│   │   └── token_models.py (Pydantic: Stake, Reward)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py (SQLAlchemy connection)
│   │   ├── models.py (SQLAlchemy ORM models)
│   │   └── migrations/ (Alembic migrations)
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── price_predictor.py (XGBoost, ARIMA models)
│   │   ├── anomaly_detector.py (Isolation Forest)
│   │   ├── strategy_evaluator.py (Ensemble predictions)
│   │   └── training_data/ (datasets for models)
│   ├── blockchain/
│   │   ├── __init__.py
│   │   ├── rpc_clients.py (ethers.js, web3.py connections)
│   │   ├── contract_abi/ (JSON ABIs)
│   │   │   ├── TST_ABI.json
│   │   │   ├── Airdrop_ABI.json
│   │   │   └── Escrow_ABI.json (Phase 2)
│   │   └── operations.py (broadcast, sign, verify)
│   ├── messaging/
│   │   ├── __init__.py
│   │   └── ably_client.py (Ably channel setup)
│   ├── storage/
│   │   ├── __init__.py
│   │   └── ipfs_client.py (Pinata integration)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py (structured logging)
│   │   ├── validators.py (input validation)
│   │   └── helpers.py (utility functions)
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py (pytest fixtures)
│       ├── test_wallet_service.py
│       ├── test_perception_service.py
│       ├── test_memory_service.py
│       ├── test_risk_service.py
│       ├── test_strategy_service.py
│       ├── test_execution_service.py
│       ├── test_guardian_service.py
│       ├── test_audit_service.py
│       └── test_routes.py
│
├── contracts/
│   ├── README.md (Solidity setup)
│   ├── hardhat.config.js (Hardhat configuration)
│   ├── package.json (npm dependencies)
│   ├── contracts/
│   │   ├── TST.sol (ERC20 + staking)
│   │   ├── Airdrop.sol (1000 TST per user)
│   │   ├── Escrow.sol (multi-sig release) [Phase 2]
│   │   ├── Router.sol (cross-chain) [Phase 2]
│   │   └── interfaces/ (IToken, IEscrow, etc.)
│   ├── test/
│   │   ├── TST.test.js
│   │   ├── Airdrop.test.js
│   │   └── integration.test.js
│   ├── scripts/
│   │   ├── deploy_bsc.js (BSC mainnet)
│   │   ├── deploy_testnet.js (BSC testnet)
│   │   └── verify_contracts.js (Etherscan verification)
│   └── deployments/ (stored deployment data)
│
├── frontend/
│   ├── package.json (React dependencies)
│   ├── tsconfig.json (TypeScript config)
│   ├── next.config.js (Next.js config)
│   ├── tailwind.config.ts (Tailwind config)
│   ├── .env.example (frontend env vars)
│   ├── public/
│   │   ├── logo.svg
│   │   ├── favicon.ico
│   │   └── assets/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── _app.tsx (Next.js app wrapper)
│   │   │   ├── _document.tsx
│   │   │   ├── index.tsx (landing page)
│   │   │   ├── signup.tsx
│   │   │   ├── wallet.tsx (Feature 1: Wallet dashboard)
│   │   │   ├── control-plane.tsx (Feature 2: Entity dashboard)
│   │   │   ├── audit.tsx (Feature 3: Audit trail)
│   │   │   ├── token.tsx (Feature 5: TST staking)
│   │   │   ├── profile.tsx (user settings)
│   │   │   └── api/ (API routes, if any)
│   │   ├── components/
│   │   │   ├── Layout/ (header, footer, nav)
│   │   │   ├── Wallet/
│   │   │   │   ├── WalletConnect.tsx
│   │   │   │   ├── BalanceCard.tsx
│   │   │   │   ├── UnifiedDashboard.tsx
│   │   │   │   └── SendModal.tsx
│   │   │   ├── ControlPlane/
│   │   │   │   ├── EntityStatus.tsx
│   │   │   │   ├── DecisionQueue.tsx
│   │   │   │   ├── ExecutionMonitor.tsx
│   │   │   │   └── ControlButtons.tsx
│   │   │   ├── Guardian/
│   │   │   │   ├── GuardianAlert.tsx
│   │   │   │   └── AnomalyDetails.tsx
│   │   │   ├── Audit/
│   │   │   │   ├── DecisionTimeline.tsx
│   │   │   │   ├── DecisionDetail.tsx
│   │   │   │   └── ExportButton.tsx
│   │   │   ├── Token/
│   │   │   │   ├── TokenBalance.tsx
│   │   │   │   ├── StakingForm.tsx
│   │   │   │   └── RewardsCalculator.tsx
│   │   │   └── Common/
│   │   │       ├── Loading.tsx
│   │   │       ├── Error.tsx
│   │   │       └── Modal.tsx
│   │   ├── lib/
│   │   │   ├── api.ts (API client)
│   │   │   ├── blockchain.ts (ethers.js helpers)
│   │   │   └── utils.ts (utility functions)
│   │   ├── hooks/
│   │   │   ├── useWallet.ts (wallet connection)
│   │   │   ├── useBalance.ts (fetch balances)
│   │   │   ├── useDecisions.ts (subscribe to decisions)
│   │   │   └── useGuardian.ts (anomaly checks)
│   │   ├── store/
│   │   │   └── zustand/
│   │   │       ├── wallet.ts (wallet state)
│   │   │       ├── decisions.ts (decision state)
│   │   │       ├── ui.ts (UI state)
│   │   │       └── index.ts (store exports)
│   │   ├── types/
│   │   │   └── index.ts (TypeScript types)
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   └── components.css
│   │   └── __tests__/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── utils/
│   │       └── integration/
│
├── .github/
│   └── workflows/
│       ├── backend_tests.yml (pytest on push)
│       ├── frontend_tests.yml (vitest on push)
│       ├── contract_tests.yml (hardhat on push)
│       ├── deploy_staging.yml (Fly.io staging)
│       └── deploy_prod.yml (Fly.io production)
│
├── infrastructure/
│   ├── fly.toml (Fly.io config for each service)
│   ├── docker-compose.yml (local entity testing)
│   ├── nginx.conf (load balancer)
│   └── scripts/
│       ├── setup_db.sh (create PostgreSQL tables)
│       ├── setup_redis.sh (Redis cluster)
│       └── setup_ipfs.sh (Pinata integration)
│
├── .gitignore (standard Python + Node.js)
├── README.md (project overview)
├── LICENSE (MIT or similar)
└── .env.example (template for all env vars)
```

---

## PHASE 0 WEEK 1-2 TASKS

### Infrastructure Setup (Week 1)

```bash
# 1. Initialize GitHub repository
git init
git add .
git commit -m "Initial commit: architecture docs"
git remote add origin https://github.com/[user]/tradesynapse.git
git push -u origin main

# 2. Create .env.example
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:port

# Blockchain RPCs
BSC_RPC=https://...
POLYGON_RPC=https://...
TRON_RPC=https://...
MASTER_WALLET_SEED=24-word-bip39-seed

# Third-party APIs
ABLY_API_KEY=...
PINATA_API_KEY=...
PINATA_API_SECRET=...
WALLETCONNECT_PROJECT_ID=...

# Services
PERCEPTION_SERVICE_URL=...
MEMORY_SERVICE_URL=...
RISK_SERVICE_URL=...
STRATEGY_SERVICE_URL=...
EXECUTION_SERVICE_URL=...
SIGNING_SERVICE_URL=...
EOF

# 3. Set up Fly.io apps (create 5 + 1 for signing)
flyctl app create tradesynapse-perception
flyctl app create tradesynapse-memory
flyctl app create tradesynapse-risk
flyctl app create tradesynapse-strategy
flyctl app create tradesynapse-execution
flyctl app create tradesynapse-signing

# 4. Set up Neon PostgreSQL
# Go to https://console.neon.tech
# Create project → Copy connection string to .env

# 5. Set up Upstash Redis
# Go to https://console.upstash.com
# Create database → Copy URL to .env

# 6. Set up Pinata IPFS
# Go to https://pinata.cloud
# Create API key → Copy to .env

# 7. Set up Vercel
vercel link
```

### Architecture Docs (Week 2)

Create these files (in order):

1. **docs/DATABASE_SCHEMA.md**
   - Full PostgreSQL schema (12+ tables)
   - Indexes, constraints, relationships
   - Sample queries

2. **docs/API_CONTRACTS.md**
   - 25+ endpoint definitions
   - Request/response formats (JSON)
   - Error codes + status codes
   - Example curl commands

3. **docs/SMART_CONTRACTS.md**
   - Solidity code for TST, Airdrop, Escrow
   - Constructor args
   - Public functions
   - Events + modifiers

4. **docs/FRONTEND_ROUTES.md**
   - Page structure
   - Component hierarchy
   - Data flow diagrams
   - URL patterns

5. **docs/ENTITY_COMMUNICATION.md**
   - Ably channel structure
   - Message formats
   - Timing/frequency
   - Error handling

6. **docs/SECURITY_CHECKLIST.md**
   - Code review checklist
   - Deployment security
   - Smart contract checks
   - API security

7. **docs/TESTING_STRATEGY.md**
   - Unit test requirements
   - Integration test plan
   - Load test scenarios
   - Test data setup

8. **docs/DEPLOYMENT.md**
   - Staging environment setup
   - Production deployment steps
   - Rollback procedures
   - Monitoring setup

9. **docs/MONITORING.md**
   - Dashboards to build
   - Alerts to set up
   - Metrics to track
   - Incident response

---

## DIRECTORY CREATION COMMANDS

To set up the full structure:

```bash
# Backend
mkdir -p backend/{config,services,routes,models,db/migrations,ml/training_data,blockchain/contract_abi,messaging,storage,utils,tests}

# Contracts
mkdir -p contracts/{contracts/interfaces,test,scripts,deployments}

# Frontend
mkdir -p frontend/src/{pages,components/{Layout,Wallet,ControlPlane,Guardian,Audit,Token,Common},lib,hooks,store/zustand,types,styles,__tests__/{components,hooks,utils,integration}}

# Infrastructure
mkdir -p infrastructure/scripts

# Docs (already done, but completing)
mkdir -p docs
```

---

## DEPENDENCIES TO INSTALL

### Backend (Python 3.12)

```bash
cd backend
python -m venv venv
source venv/bin/activate

pip install \
  fastapi==0.109.0 \
  uvicorn==0.27.0 \
  sqlalchemy==2.1.0 \
  psycopg2-binary==2.9.9 \
  pydantic==2.5.0 \
  python-dotenv==1.0.0 \
  web3==6.15.0 \
  ethers==0.2.11 \
  pandas==2.1.0 \
  numpy==1.26.0 \
  scikit-learn==1.3.0 \
  xgboost==2.0.0 \
  lightgbm==4.1.0 \
  statsmodels==0.14.0 \
  ably==1.2.6 \
  aiohttp==3.9.0 \
  pytest==7.4.3 \
  pytest-asyncio==0.21.1

pip freeze > requirements.txt
```

### Frontend (Node.js 20)

```bash
cd frontend
npm init -y

npm install \
  next@16.1.6 \
  react@18.3.0 \
  react-dom@18.3.0 \
  typescript@5.4.0 \
  tailwindcss@3.4.0 \
  zustand@4.5.0 \
  @tanstack/react-query@5.40.0 \
  wagmi@2.6.0 \
  viem@2.10.0 \
  @web3modal/wagmi@4.1.0 \
  ethers@6.10.0

npm install --save-dev \
  vitest@1.1.0 \
  playwright@1.45.0 \
  eslint@8.55.0 \
  prettier@3.1.0
```

### Contracts (Node.js)

```bash
cd contracts
npm install \
  hardhat@2.19.0 \
  @nomicfoundation/hardhat-toolbox@4.0.0 \
  @openzeppelin/contracts@4.9.3 \
  dotenv@16.3.1

npm install --save-dev \
  solhint@4.1.0 \
  @nomiclabs/hardhat-ethers@2.2.3
```

---

## CRITICAL SETUP NOTES

1. **Master Seed:** Keep in HSM or `.env.local` (never commit)
2. **Database:** Initialize with schemas (don't use auto-migration)
3. **Smart Contracts:** Deploy to testnet first, audit before mainnet
4. **Secrets:** Use Fly.io secrets CLI, not .env files
5. **Monitoring:** Set up before first production deploy

---

**Version:** 1.0  
**Ready:** Yes, next AI can use this to set up  
**Next step:** Create these files after this week's infrastructure setup
