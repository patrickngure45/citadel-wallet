# Citadel: Quick Reference Guide

**For: Any AI Agent Starting Work on This Project**

*Powered by TradeSynapse Protocol*

---

## 🎯 WHAT IS CITADEL?

Your autonomous capital fortress using 5 independent AI entities (TradeSynapse Protocol) to manage yield farming, arbitrage, and P2P lending across 3 blockchains (BSC, Polygon, Tron) for emerging market users.

**Unique differentiators:**
- 5-entity governance (not single algorithm)
- 50/50 profit sharing (not fixed fees)
- Multi-chain by default (not Ethereum-only)
- Discipline-focused UI (not hype-driven)
- Full transparency + audit trail (IPFS immutable)

---

## 📋 THE 3 CRITICAL DOCUMENTS

Read these IN ORDER:

1. **PROJECT_MANIFEST.md** - What we're building (sections 1-8 essential)
2. **IMPLEMENTATION_ROADMAP.md** - How we're building it (phases 0-1 focus)
3. **PROGRESS_TRACKER.md** - What's done, what's not (status updates)

This document (QUICK_REFERENCE.md) - Use as cheat sheet while working

---

## 🏗️ ARCHITECTURE IN 30 SECONDS

```
User connects MetaMask
    ↓
Backend derives wallet (BIP44, deterministic)
    ↓
5 async services (Perception → Memory → Risk → Strategy → Execution)
    ↓
Each service updates via Ably channels (not direct calls)
    ↓
Strategy service queues decisions (ranked by confidence)
    ↓
Execution broadcasts to blockchain (BSC, Polygon, Tron)
    ↓
All decisions logged to IPFS (immutable audit trail)
    ↓
User sees results + reasoning on dashboard
```

**Key:** Services run independently at different speeds (30s, 5m, 3m, 2m, 1m)
This prevents feedback loops and keeps decisions sane.

---

## 🚀 PHASE 1 MVP (5 Features, 8 Weeks)

| Week | Feature | Priority |
|------|---------|----------|
| 3-4 | Multi-Chain Wallet | 🔴 First |
| 5-6 | Control Plane (entity dashboard) | 🔴 First |
| 6 | Audit Trail (IPFS logging) | 🟠 Second |
| 7 | Guardian (anomaly detection) | 🟠 Second |
| 8 | TST Token (staking + airdrop) | 🟡 Nice-to-have |

**NOT in Phase 1:**
- ❌ P2P matching (too complex)
- ❌ Cross-border router (too complex)
- ❌ Escrow contracts (needs P2P first)

---

## 💾 DATABASE SCHEMA ESSENTIALS

**Must have:**
```sql
-- User management
users (id, email, risk_profile, aum, created_at)

-- Wallet management
users_wallets (id, user_id, bsc_addr, polygon_addr, tron_addr)
wallet_balances (id, wallet_id, chain, token, balance_usd, updated_at)

-- Decision tracking
decisions (id, user_id, strategy, amount, chain, confidence, status, tx_hash)
entity_logs (id, user_id, entity_name, action, output, timestamp)

-- Guardian protection
guardian_checks (id, user_id, tx_hash, anomaly_score, status, approved_at)

-- Token system
token_stakes (id, user_id, amount, stake_time, reward_amount)
```

**See:** docs/DATABASE_SCHEMA.md (to be created)

---

## 🔌 API ENDPOINTS (MVP)

**Wallet:**
- `POST /wallet/create` - Derive wallets for user
- `GET /wallet/{id}/balances` - Get all chain balances

**Entity:**
- `GET /entity/{service}/status` - Is service online?
- `GET /entity/strategy/queue` - What decisions pending?
- `POST /entity/strategy/veto` - User can veto (optional)

**Execution:**
- `GET /entity/execution/history` - Completed decisions
- `GET /entity/execution/active` - Currently executing

**Guardian:**
- `POST /guardian/check` - Pre-flight anomaly check
- `POST /guardian/approve` - User approves 2FA
- `GET /guardian/pending` - Pending approvals

**Audit:**
- `GET /audit/export` - Download all decisions (JSON)
- `GET /audit/hash` - Get IPFS hash

**Token:**
- `POST /token/claim-airdrop` - Claim 1,000 TST
- `POST /token/stake` - Deposit TST for staking
- `POST /token/unstake` - Withdraw + claim rewards

**See:** docs/API_CONTRACTS.md (to be created)

---

## 🔐 SECURITY GOLDEN RULES

1. **Never expose private keys** in API responses
   - Derive on-demand in Signing Service only
   - Delete from memory immediately after use

2. **Always log decisions** to IPFS
   - Weekly Merkle tree
   - User can verify immutability

3. **Guardian must block suspicious txs**
   - 3am transfers, new addresses, VPN
   - Require 2FA confirmation (MetaMask sign)

4. **Smart contracts must be audited**
   - Before mainnet deployment
   - Budget: $30k-50k (external firm)

5. **Entity communication is async only**
   - No synchronous calls between services
   - Use Ably channels for messaging

---

## 💰 TECH STACK (Don't Change)

**Frontend:**
```
Next.js 16.1.6 (Turbopack)
React 18.3
TypeScript 5.4
Tailwind 3.4
shadcn/ui
WalletConnect 3.0
Vercel (hosting)
```

**Backend:**
```
FastAPI 0.109
Python 3.12
SQLAlchemy 2.1
Pydantic 2.5
PostgreSQL 16 (Neon)
Redis (Upstash)
Fly.io (hosting - 5 services)
```

**Blockchain:**
```
ethers.js v6
web3.py 6.15
wagmi 2.6
viem 2.10
Solidity 0.8.19
```

---

## 🎓 ENTITY SYSTEM DEEP DIVE

### Perception Service
- **Job:** Real-time market data (prices, volumes, spreads)
- **Speed:** 30 seconds per tick
- **Output:** Price feeds with confidence scores
- **Authority:** Read-only (no decisions)

### Memory Service
- **Job:** Learn patterns, forecast prices
- **Speed:** 5 minutes per analysis (intentionally slow)
- **Output:** Pattern recognition + forecasts
- **Authority:** Suggest patterns (no veto)
- **Models:** XGBoost, LightGBM, ARIMA

### Risk Service
- **Job:** Validate strategies, weight confidence
- **Speed:** 3 minutes per cycle
- **Output:** Confidence weights (not veto flags)
- **Authority:** Reduce size if risky (collaborative, not blocking)

### Strategy Service
- **Job:** Generate decision queue ranked by confidence
- **Speed:** 2 minutes per cycle
- **Output:** Ordered list of proposed strategies
- **Authority:** Propose only (no execution)

### Execution Service
- **Job:** Broadcast decisions to blockchain
- **Speed:** 1 minute per cycle
- **Output:** Transaction confirmations
- **Authority:** Execute blindly (follow orders)

### Signing Service (Isolated)
- **Job:** Hold master seed, sign transactions
- **Speed:** On-demand
- **Output:** Signed transactions only
- **Authority:** Cryptographic signing only

---

## 🧠 ML/PREDICTION ESSENTIALS

**Models to build:**

1. **Price Prediction (5min ahead)**
   - Input: Price history + volume + on-chain metrics
   - Output: Price forecast + confidence (0-1)
   - Model: XGBoost or LightGBM
   - Accuracy target: 65%+

2. **Anomaly Detection**
   - Input: Transaction details (time, amount, address, IP, etc.)
   - Output: Anomaly score (0-100)
   - Model: Isolation Forest or Local Outlier Factor
   - Threshold: 70% = pause + 2FA required

3. **Strategy Success Prediction**
   - Input: Market state + strategy params
   - Output: Win probability (0-1)
   - Model: Ensemble (XGBoost + Random Forest + LSTM)
   - Accuracy target: 70%+

**Data needs:**
- 3+ years historical price data (for backtesting)
- 1000+ labeled transaction examples (for anomaly detection)
- 500+ past strategy executions (for success prediction)

---

## 📊 MONITORING CHECKLIST

Keep these dashboards live:

```
Entity Health:
  - All 5 services online? ✓
  - Last update timestamps
  - Error rates

Decision Quality:
  - Win rate (% profitable)
  - Average return
  - Max drawdown

User Protection:
  - Guardian alerts this week
  - False positives (blocked good txs)
  - False negatives (missed bad txs)

System Performance:
  - API latency (target: <200ms)
  - Database connections healthy
  - IPFS upload success rate
```

---

## 🚨 COMMON MISTAKES TO AVOID

❌ **Don't:**
- Redesign the 5-entity system (it works)
- Add Phase 2 features before Phase 1 is done
- Make synchronous calls between entities (breaks async design)
- Skip IPFS logging (audit trail is mandatory)
- Forget that users need 2FA for suspicious txs
- Use guaranteed return language ("12% guaranteed" = illegal)
- Deploy contracts to mainnet without audit
- Code without writing docs first

✅ **Do:**
- Keep entities async + independent
- Log every decision to IPFS
- Test with backtesting before live trading
- Monitor model accuracy (revert if < 60%)
- Circuit break on large drawdowns (>10%)
- Be transparent about risks
- Audit code + contracts before launch
- Write docs → design DB → design API → then code

---

## 📈 SUCCESS METRICS (Year 1)

By end of year 1, we need:
- 1,000 users
- $50M AUM
- $5M+ ARR
- 10-12% average user returns
- 99.5% uptime
- Zero security incidents

---

## 🔄 WORKFLOW FOR THIS PROJECT

**Correct sequence (DO THIS):**
1. Create `DATABASE_SCHEMA.md` ← Start here
2. Create `API_CONTRACTS.md` ← Then this
3. Create `SMART_CONTRACTS.md` ← Then this
4. Create GitHub repo + infrastructure ← Then this
5. Start building Feature 1 (Wallet) ← Then this
6. Build Features 2-5 in order ← Then this

**Incorrect sequence (DON'T DO THIS):**
❌ Start coding immediately
❌ Skip architecture docs
❌ Add Phase 2 features early
❌ Change the entity system
❌ Ignore the 5-feature limit

---

## 🆘 IF YOU GET STUCK

**"What should I build next?"**
→ Read IMPLEMENTATION_ROADMAP.md, see what week you're in

**"How does the entity system work?"**
→ Read PROJECT_MANIFEST.md section 2 + this document's entity deep dive

**"What's the database schema?"**
→ DATABASE_SCHEMA.md (ask me to create if not yet made)

**"Should I add this feature?"**
→ Is it in Phase 1 (5 features)? If no, defer to Phase 2

**"How do I know my code is good?"**
→ Check TESTING_STRATEGY.md (85%+ test coverage required)

**"Should I change X?"**
→ Is it listed in "CRITICAL DECISIONS" section of PROJECT_MANIFEST.md? If yes, don't change it.

---

## 📞 HANDOFF PROTOCOL

When starting a new chat session:

1. **First action:** Read this document
2. **Second action:** Read PROJECT_MANIFEST.md
3. **Third action:** Read PROGRESS_TRACKER.md
4. **Then:** Look at IMPLEMENTATION_ROADMAP.md for current week
5. **Finally:** Check what docs still need to be created (DATABASE_SCHEMA, API_CONTRACTS, etc.)

**Always ask:**
- "What week/phase are we in?"
- "What feature should I work on?"
- "What's already been documented?"
- "What docs need to be created next?"

---

## ✅ READY CHECKLIST

Before starting any coding:
- [ ] Read all 3 main docs (Manifest, Roadmap, Tracker)
- [ ] Understand the 5-entity system
- [ ] Know the 8 features (5 in Phase 1, 3 in Phase 2)
- [ ] Understand tech stack (no changes)
- [ ] Know what database tables are needed
- [ ] Know what API endpoints are needed
- [ ] Know security golden rules
- [ ] Understand monitoring/testing requirements
- [ ] Know not to start coding until docs are done

---

**Document Version:** 1.0  
**Purpose:** Prevent context loss across AI sessions  
**Audience:** Any AI agent working on TradeSynapse  
**Last Updated:** January 30, 2026
