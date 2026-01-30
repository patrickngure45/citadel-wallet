# Citadel: Complete Project Manifest

**Last Updated:** January 30, 2026  
**Brand:** Citadel (The Fortress)  
**Protocol:** TradeSynapse (5-Entity Autonomous System)  
**Status:** PRE-BUILD (Architecture Complete, No Code Yet)  
**Owner:** User  
**Token Budget Warning:** This document is handoff-ready for new AI agents

---

## 1. EXECUTIVE SUMMARY

**What is Citadel?**

Your autonomous capital fortress that uses 5 independent AI entities (TradeSynapse Protocol) to orchestrate multi-chain yield farming, P2P lending, and arbitrage on behalf of users. Unlike passive yield products (Yearn) or trading bots (3Commas), TradeSynapse:
- Makes decisions using collaborative entity governance (not centralized algorithm)
- Operates across 3 blockchains simultaneously (BSC, Polygon, Tron)
- Matches P2P capital through AI coordination (not manual)
- Protects users with Guardian anomaly detection
- Shares 50% of profits with users (aligned incentives)

**Target User:**
- Emerging market investors ($50k-$500k capital)
- Comfortable with DeFi, want hands-off management
- Care about discipline over moonshots
- Want transparent audit trails for taxes/compliance

**Revenue Model:**
- 50% of trading profits
- Escrow fees (0.1% per P2P match)
- Premium features ($19-199/month subscriptions)
- Expected: $5.1M+ ARR at 1,000 users

---

## 2. CORE ARCHITECTURE

### Entity System (5 Services)

```
┌─────────────┐     ┌──────────┐     ┌───────┐     ┌──────────┐     ┌───────────┐
│ PERCEPTION  │────▶│  MEMORY  │────▶│ RISK  │────▶│ STRATEGY │────▶│ EXECUTION │
│ (Live Data) │     │(Patterns)│     │(Veto) │     │(Propose) │     │ (Execute) │
└─────────────┘     └──────────┘     └───────┘     └──────────┘     └───────────┘
    30s              5min             3min          2min              1min
   (FAST)           (SLOW)           (MEDIUM)      (FAST)           (MEDIUM)

Key Properties:
- Async (no feedback loops, each runs independently)
- Unidirectional (Perception → Memory → Risk → Strategy → Execution)
- Non-trusting (Risk doesn't trust Strategy's confidence)
- Speed mismatch prevents reflexivity (old data used intentionally)
```

**Entity Responsibilities:**

| Entity | Input | Output | Authority |
|--------|-------|--------|-----------|
| **Perception** | Market data (CEX, DEX, on-chain) | Price feeds + freshness score | Read-only |
| **Memory** | Perception output + historical data | Pattern recognition + forecasts | Suggest patterns |
| **Risk** | All previous outputs + constraints | Confidence weighting (no veto, soft weights) | Adaptive sizing |
| **Strategy** | Market conditions + patterns + risk scores | Decision queue (ranked by confidence) | Propose only |
| **Execution** | Decision queue | Broadcast to blockchain | Execute blindly |

---

## 3. TECHNOLOGY STACK (2026 Latest)

### Frontend
```
Framework:      Next.js 16.1.6 (Turbopack)
Runtime:        React 18.3
Language:       TypeScript 5.4 (strict mode)
Styling:        Tailwind CSS 3.4
Components:     shadcn/ui + custom
State:          Zustand 4.5
Data fetching:  TanStack Query 5.40
Blockchain UI:  WalletConnect 3.0, web3Modal 5.0
Hosting:        Vercel (auto-deploy from GitHub)
```

### Backend
```
Framework:      FastAPI 0.109
Language:       Python 3.12
ORM:            SQLAlchemy 2.1
Validation:     Pydantic 2.5
Database:       PostgreSQL 16 (Neon)
Cache:          Redis (Upstash)
Real-time:      Ably channels (async messaging between entities)
File storage:   IPFS (Pinata) for audit logs
Hosting:        Fly.io (5 services: Perception, Memory, Risk, Strategy, Execution)
```

### Blockchain
```
EVM Chains:     BSC, Polygon, Tron
Libraries:      ethers.js v6, web3.py 6.15, wagmi 2.6, viem 2.10
Smart contracts: Solidity 0.8.19
DEX access:     Uniswap v4, Curve, Balancer
Bridges:        Stargate, Across, Synapse
```

### ML/AI
```
ML models:      XGBoost, LightGBM, Random Forest (price prediction)
Time series:    ARIMA, Prophet (5min, 30min, 1h forecasts)
Deep learning:  LSTM (optional, for advanced predictions)
LLM:            Claude (sentiment analysis, decision explanation)
Libraries:      scikit-learn, pandas, numpy, scipy
```

### Testing & Monitoring
```
Frontend:       Vitest 1.1, Playwright 1.45
Backend:        pytest, pytest-asyncio
Integration:    Docker for local entity testing
Monitoring:     Datadog or equivalent (logs, metrics, alerts)
```

---

## 4. FEATURES (8 Core)

| # | Feature | User Action | Expected ROI | Complexity |
|---|---------|-------------|--------------|-----------|
| 1 | **Autonomous Control Plane** | Set risk tolerance → AI manages capital | None (infrastructure) | High |
| 2 | **P2P Capital Agreements** | Declare capital need → AI matches → escrow locks funds | 0.1% fee per match | High |
| 3 | **Cross-Border Router** | Say "send $5k to Polygon" → AI picks best route | 0.1-0.5% optimization | Medium |
| 4 | **Wallet Guardian** | Anomaly detected → transfer paused → 2FA approve | Prevents losses (1-5% annually) | Medium |
| 5 | **Escrow & Settlements** | Smart contracts release funds on conditions | 0.1% fee per settlement | High |
| 6 | **Decision Log & Audit** | Every decision logged to IPFS | Tax efficiency, compliance | Low |
| 7 | **TST Token Rewards** | Free tokens on signup + earn via activity | Gamification + utility | Medium |
| 8 | **Multi-Chain Wallets** | See all wallets (BSC, Polygon, Tron) unified | UX improvement | Low |

---

## 5. WALLET SYSTEM

### Master Wallet (MetaMask)
- User's personal wallet (guardian signer)
- Approves critical transactions via WalletConnect
- Can emergency-stop any strategy

### Derived Wallets (Backend-owned)
```
Master Seed (24-word BIP39, in HSM)
├─ User Wallets: m/44'/60'/0'/0/[user_id]
│  └─ Used for: Deploying capital, receiving yields
│
├─ Escrow Wallets: m/44'/60'/0'/1/[agreement_id]
│  └─ Used for: Locking funds in P2P contracts
│
├─ Risk Vault: m/44'/60'/0'/2/0
│  └─ Used for: Emergency reserves, liquidation buffer
│
└─ Liquidity Pool: m/44'/60'/0'/3/0
   └─ Used for: Shared LP positions

Key Properties:
- Deterministic (same seed = same wallets every time)
- Multi-chain compatible (same key on BSC + Polygon)
- Tron encoding different (special derivation for Tron)
- User never sees private key (derived on-demand for signing)
- 30-day custody window (TradeSynapse holds keys), then user can request
```

---

## 6. TOKEN SYSTEM (TST)

### Supply Distribution
```
Total Supply: 1,000,000 TST

40% Treasury (400,000)     → Operations, marketing, ecosystem
20% Team (200,000)         → 4-year vesting, cliff 1-year
15% Investors (150,000)    → Early funding round
15% Community (150,000)    → Airdrops, rewards, ecosystem
10% Liquidity (100,000)    → DEX bootstrap
```

### User Acquisition
```
Per user signup: 1,000 TST free (locked 30 days)
Unlock accelerators:
├─ Use Perception services: +250 TST (1-week lockup)
├─ Execute P2P deal: +250 TST (1-week lockup)
├─ Use Escrow: +250 TST (1-week lockup)
├─ Staking: 5-12% APY on locked TST
└─ Full unlock: After 30 days + participation

Fees: 30-50% discount with TST staking
```

---

## 7. DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                    │
└─────────────────────────────────────────────────────────────┘

FRONTEND (Vercel)
├─ Next.js 16 auto-deployed from GitHub
├─ Serverless functions for API calls
├─ CDN for static assets globally
└─ Auto-scaling, zero downtime deploys

BACKEND (Fly.io - 5 separate services)
├─ Perception Service: ethers.js → DEX/CEX APIs
│  └─ dyno count: 2 (one on east, one on west)
│
├─ Memory Service: Historical analysis + ML models
│  └─ dyno count: 1 (CPU-intensive, scheduled)
│
├─ Risk Service: Validation + weighting logic
│  └─ dyno count: 2 (duplicated for reliability)
│
├─ Strategy Service: Decision proposer
│  └─ dyno count: 1 (stateless, can scale)
│
├─ Execution Service: Blockchain broadcaster
│  └─ dyno count: 2 (queue-based, distributed)
│
└─ Signing Service (ISOLATED)
   └─ dyno count: 1 (HSM protected, minimal exposure)

DATABASE (Neon PostgreSQL)
├─ Replication: Primary + 2 standby
├─ Backups: Hourly + point-in-time recovery
├─ Monitoring: Connection pooling via PgBouncer
└─ Scaling: Read replicas for analytics

CACHE (Upstash Redis)
├─ Entity message queue (Ably fallback)
├─ Decision cache (avoid redundant computations)
├─ Rate limiting (prevent spam)
└─ Session storage

FILE STORAGE (Pinata IPFS)
├─ Decision logs (immutable audit trail)
├─ Smart contract ABIs
├─ User documents (audit exports)
└─ Replicated across 3 IPFS nodes

SMART CONTRACTS (Multi-chain)
├─ BSC:     TST token, escrow, staking
├─ Polygon: Routing, cross-chain bridges
├─ Tron:    P2P lending pools
└─ All verified on explorers, not upgraded post-launch
```

---

## 8. REVENUE STREAMS

### User-Facing Revenue

| Module | Mechanism | Per $100k Capital | Monthly | Annual |
|--------|-----------|------------------|---------|--------|
| Profit Share | 50/50 split on user gains | $50/month | $50 | $600 |
| Escrow Fees | 0.1% per P2P match | $20 (4 matches) | $80 | $960 |
| Cross-border Routing | 0.05-0.1% per route | $30 (24 routes) | $120 | $1,440 |
| Wallet Guardian | $0.50 per block | $10 (20 alerts) | $40 | $480 |
| P2P Lending Interest | 50% of 8% APY earned | $333 | $333 | $4,000 |
| TST Token Staking | 8% APY on staked TST | Variable | Variable | $80K (10M TST @ $0.10) |
| **User Revenue Total** | | | **$633** | **$7,560** |

### Developer Ecosystem Revenue

| Channel | Model | Year 1 | Year 2 | Year 3 |
|---------|-------|--------|--------|--------|
| Pro API Subscriptions | $99/mo × developers | $59.4K | $356.4K | $950.4K |
| Enterprise API Deals | $20K/mo × partnerships | $360K | $2.4M | $7.5M |
| Marketplace Fees | 20% cut on strategy profits | $50K | $500K | $3M |
| White-Label Revenue Share | 20% of partner profits | $100K | $600K | $1.5M |
| **Developer Revenue Total** | | **$569.4K** | **$3.856M** | **$13M+** |

**Scale to 1,000 users + 300+ developers:**
- Conservative (Year 1): $4.4M ARR
- Realistic (Year 2): $7.8M+ ARR
- Best case (Year 3): $13M+ ARR

---

## 8.5 DEVELOPER ECOSYSTEM (New!)

### Three-Tier API Model

**Tier 1: Free API** (Ecosystem play)
- 100 requests/day, read-only
- Perfect for learning, testing, side projects
- No commercial restrictions after Pro upgrade
- Community support via Discord
- Goal: Attract 500+ developers by Year 1

**Tier 2: Pro API** ($99/month)
- 10,000 requests/day, read + write
- Webhooks, custom integrations
- Production-grade SLA (99.5%)
- Priority email support
- Goal: 300+ paid subscriptions by Year 2

**Tier 3: Enterprise API** (Custom pricing)
- Unlimited requests, white-label support
- Custom strategies, dedicated support
- Revenue share: 80/20 (Enterprise gets 80% of profits)
- Partnerships with exchanges, wealth managers
- Goal: 10+ enterprise deals by Year 2

### Developer Marketplace (Phase 2)

**Concept:** Developers publish trading strategies, users install them
- Revenue split: 70% Creator, 20% Citadel, 10% Network
- Example: "ML Momentum Strategy" by @TradeDev generates $1,000 profit → TradeDev gets $700

**Marketplace Economics:**
- Year 1: 10 strategies, $50K revenue
- Year 2: 100 strategies, $500K revenue
- Year 3: 500+ strategies, $3M+ revenue

### SDK Support
- **JavaScript/TypeScript** (`@citadel/api`)
- **Python** (`citadel-api`)
- **Web3.js** (ethers.js integration)
- **CLI Tool** (`citadel-cli` for testing)

### Developer Experience
- Interactive API explorer (Swagger UI)
- Code examples in 3+ languages
- Webhook testing sandbox
- GitHub discussions + Discord community
- Monthly webinars + quarterly hackathons ($50K prizes)

**See:** `DEVELOPER_API_STRATEGY.md` for complete details

---

## 9. SECURITY CONSIDERATIONS

### Key Protection
```
Master seed: Hardware Security Module (HSM) only
├─ Never in plain text
├─ Never in environment variables
├─ Rotated quarterly
└─ Backup in secure vault (multi-sig)

Signing Service:
├─ Isolated process (separate dyno)
├─ Rate-limited (1000 txns/hour per user)
├─ Audit all signatures
├─ Key deleted immediately after use
```

### Smart Contract Security
```
All contracts:
├─ Audited by professional firm (budget: $30k-50k)
├─ Coverage: Escrow, routing, staking
├─ Not upgraded post-launch (immutable)
├─ Admin functions removed or time-locked
└─ Insurance coverage (Nexus Mutual optional)
```

### User Protection
```
Guardian:
├─ Detects 3am transfers, new addresses, VPN
├─ Pauses until 2FA confirmation via MetaMask
├─ Costs: $0.50 per block (built into profits)

Escrow:
├─ Multi-sig release (2-of-3: Perception, user, counterparty)
├─ Time-locked (if dispute, funds locked for cooling-off)

Audit Trail:
├─ Every decision logged immutably
├─ User can export proof of execution (for tax audits)
├─ Recoverable if system fails
```

---

## 10. REGULATORY & LEGAL

### Jurisdiction Strategy
```
Frontend: Global (no license needed, just software)
Backend: Fly.io US-based (compliant with FinCEN)
Smart Contracts: Code is law (no license needed)

Compliance:
├─ No guaranteed returns (we say "realistic range 6-18%")
├─ Not offering investment advice (user sets parameters)
├─ Not custodian (user retains ownership, we execute)
├─ OFAC screening on user addresses
└─ KYC only if TradeSynapse grows to $100M+ AUM

TO-DO: Legal review before launch (budget: $5k-10k)
```

---

## 11. TIMELINE & PHASES

### Phase 0: Design & Setup (Weeks 1-2)
- [x] Architecture finalized
- [x] 8 features defined
- [ ] Database schema created
- [ ] API contracts defined
- [ ] Smart contract specs written
- [ ] Deployment infrastructure set up

### Phase 1: MVP (Weeks 3-8)
**Launch with 5 features (in priority order):**

1. **Multi-Chain Wallet Management** (foundational)
   - Connect MetaMask
   - Derive user wallets
   - Show unified view of BSC, Polygon, Tron balances

2. **Autonomous Control Plane** (core)
   - Dashboard showing entity decisions
   - Real-time strategy execution status
   - Manual pause/resume controls

3. **Decision Log & Audit Trail** (compliance)
   - Log every entity decision to IPFS
   - User can export for taxes
   - Immutable record

4. **Wallet Guardian** (protection)
   - Anomaly detection
   - Pause + 2FA on suspicious transfers
   - Simple, MVP version (expand later)

5. **TST Token Basics** (incentive)
   - Free 1,000 TST on signup
   - Staking rewards (5% APY minimum)
   - Fee discounts

**Excluded from Phase 1 (too complex):**
- P2P Capital Agreements (complex matching algorithm)
- Cross-Border Router (bridge integration complexity)
- Escrow & Conditional Settlement (complex smart contracts)

### Phase 2: Advanced Features (Weeks 9-12)
- Add P2P Capital Matching
- Add Cross-Border Router
- Add Escrow & Multi-sig Contracts
- Expand Guardian (to multiple anomaly types)

### Phase 3: Optimization (Weeks 13+)
- ML model improvements
- Entity refinement
- Scale to 1000+ users

---

## 12. CRITICAL DECISIONS (Don't Re-do These)

| Decision | Why | Alternative Rejected |
|----------|-----|----------------------|
| 5-entity system | Prevents feedback loops, enables async reasoning | Single algorithm (too rigid) |
| Async architecture | Entities run independently at different speeds | Synchronous (causes reflexivity) |
| 50/50 profit share | Aligns incentives perfectly | Fixed fees (misaligned) |
| MetaMask integration | Standard, proven, user-familiar | Direct custody (regulatory risk) |
| Derived wallets (BIP44) | Deterministic, secure, no private key to user | Random wallets (not recoverable) |
| Multi-chain (BSC+Polygon+Tron) | Emerging markets, different fee structures | Ethereum-only (already saturated) |
| IPFS for audit trail | Immutable, decentralized, audit-friendly | Centralized database (could be deleted) |
| No guaranteed returns claim | Regulatory safety, sets expectations | "12% guaranteed" (false, illegal) |
| Profit-sharing model | Sustainable, user-aligned | Subscription-only (no incentive for performance) |

---

## 13. KNOWN RISKS & MITIGATIONS

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Smart contract exploit | Critical | Audit before launch, insurance, circuit breakers |
| ML model drift | High | Continuous retraining, backtesting, monitoring |
| Regulatory crackdown | High | Legal review, no false claims, clear disclaimers |
| User wallet compromise | Medium | Guardian detection, multi-sig escrow |
| Bridge hack | Medium | Diversify bridges, limit size per route |
| Exchange API down | Low | Fallback to alternative feeds, cache data |
| Entity logic bug | High | Extensive testing, A/B testing on small subset |
| Market crash | Medium | Risk service adaptive sizing, circuit breakers |
| Team departure | Medium | Documentation (this manifest), code clarity |

---

## 14. SUCCESS METRICS (Year 1)

| Metric | Target | Current |
|--------|--------|---------|
| Users | 1,000 | 0 |
| AUM | $50M | $0 |
| ARR | $5M+ | $0 |
| Avg user return | 10-12% | TBD |
| User retention (6mo) | >60% | N/A |
| Uptime | 99.5% | N/A |
| Smart contract audits passed | 100% | 0/3 |

---

## 15. NEXT IMMEDIATE STEPS (For Next AI)

When a new AI picks up this project:

1. **Read this manifest entirely** (you're reading it)
2. **Review ARCHITECTURE_DECISIONS.md** (why each choice)
3. **Check TECH_STACK.md** (exact versions, no upgrades)
4. **Look at PROGRESS_TRACKER.md** (what's done, what's not)
5. **Start with DATABASE_SCHEMA.md** (create PostgreSQL tables)
6. **Then API_CONTRACTS.md** (define FastAPI endpoints)
7. **Then SMART_CONTRACTS.md** (write Solidity code)
8. **Then FRONTEND_COMPONENTS.md** (start Next.js pages)

---

**Document Version:** 1.0  
**Last AI to Touch:** Initial architecture agent  
**Ready for Handoff:** YES ✓  
**Can any AI pick this up:** YES ✓
