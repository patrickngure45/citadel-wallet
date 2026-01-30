# Citadel: Your Capital Fortress

**Powered by TradeSynapse Protocol**

An autonomous capital allocation system using 5 independent AI entities to orchestrate multi-chain yield farming, P2P lending, and arbitrage across BSC, Polygon, and Tron.

---

## 🏰 What is Citadel?

Citadel is your autonomous capital fortress. Deploy once, let 5 independent AI entities optimize your capital across three blockchains:

- **Perception:** Real-time market data aggregation
- **Memory:** Pattern recognition & forecasting
- **Risk:** Intelligent confidence weighting
- **Strategy:** Decision ranking & optimization
- **Execution:** Autonomous blockchain operations

**Result:** 8-18% APY (realistic), 50% of profits go to you

---

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- PostgreSQL 16
- Redis

### Development Setup

```bash
# Clone repo
git clone https://github.com/[owner]/citadel.git
cd citadel

# Copy environment template
cp .env.example .env.local

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Contracts setup
cd ../contracts
npm install
```

### Running Locally

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn app:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Smart contract testing (optional)
cd contracts
npx hardhat test
```

Open http://localhost:3000

---

## 📚 Documentation

All documentation is in `/docs`:

- **00_START_HERE.md** - Overview & quick navigation
- **QUICK_REFERENCE.md** - Developer cheat sheet
- **PROJECT_MANIFEST.md** - Complete product vision
- **IMPLEMENTATION_ROADMAP.md** - 12-week build plan
- **PROGRESS_TRACKER.md** - Current status
- **REPOSITORY_STRUCTURE.md** - Directory layout

---

## 🏗️ Architecture

### 5 Autonomous Entities (TradeSynapse Protocol)

```
Perception (30s)     Market data
    ↓
Memory (5m)          Pattern learning
    ↓
Risk (3m)            Confidence weighting
    ↓
Strategy (2m)        Decision ranking
    ↓
Execution (1m)       Blockchain broadcast
```

### Multi-Chain Strategy

- **BSC:** Arbitrage + lending + escrow
- **Polygon:** Cross-border routing + liquidity
- **Tron:** P2P matching + rewards

### Smart Contracts

- **TST Token:** ERC20 + staking rewards
- **Airdrop:** 1,000 TST per user signup
- **Escrow:** Multi-sig P2P settlements
- **Router:** Cross-chain optimization (Phase 2)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov

# Frontend tests
cd frontend
npm run test

# Contract tests
cd contracts
npx hardhat test

# Integration tests
npm run test:integration
```

**Target:** 85%+ code coverage

---

## 🚢 Deployment

### Staging (Testnet)

```bash
# Deploy smart contracts to BSC testnet
cd contracts
npx hardhat run scripts/deploy_testnet.js --network bsc-testnet

# Deploy backend to Fly.io staging
flyctl deploy --config fly.staging.toml

# Deploy frontend to Vercel staging
vercel --prod
```

### Production (Mainnet)

See `docs/DEPLOYMENT.md` for full procedure.

---

## 📊 Monitoring

- **Fly.io dashboards:** Service health & logs
- **Datadog:** Metrics & alerts
- **Neon console:** Database performance
- **IPFS explorer:** Audit trail verification

---

## 🔐 Security

- Master seed stored in HSM (production only)
- Private keys never exposed in APIs
- Guardian anomaly detection on transfers
- IPFS audit trail immutable record
- Smart contracts audited before mainnet
- Rate limiting on all services

**Report vulnerabilities:** security@citadelfi.com

---

## 📈 Roadmap

- **Week 1-2:** Infrastructure & database schema
- **Week 3-4:** Wallet Management feature
- **Week 5-6:** Autonomous Control Plane
- **Week 6:** Audit Trail logging
- **Week 7:** Wallet Guardian protection
- **Week 8:** TST Token system
- **Week 9-12:** Advanced features (P2P, Router, Escrow)

See `IMPLEMENTATION_ROADMAP.md` for details.

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit: `git commit -am 'Add feature'`
3. Push: `git push origin feature/your-feature`
4. Create Pull Request

All PRs require:
- Tests passing
- 85%+ coverage
- Code review
- No security issues

---

## 📝 License

MIT License - See LICENSE file

---

## 💬 Questions?

- Read docs in `/docs`
- Check issues for known problems
- Create new issue for bugs
- Discuss in GitHub Discussions

---

**Ready to build your capital fortress? Let's go.** 🚀

---

**Latest Update:** January 30, 2026  
**Phase:** 0 - Infrastructure Setup  
**Status:** Ready to Deploy
