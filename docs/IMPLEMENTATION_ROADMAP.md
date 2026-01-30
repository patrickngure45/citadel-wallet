# Citadel: Detailed Implementation Roadmap

**Last Updated:** January 30, 2026  
**Brand:** Citadel (The Fortress)  
**Protocol:** TradeSynapse (5-Entity System)  
**Status:** READY FOR BUILD  
**Total Estimated Duration:** 12 weeks  

---

## PHASE 0: SETUP (Weeks 1-2)

### Week 1: Foundation
- [ ] Create GitHub repository (private)
- [ ] Set up Fly.io account + 5 apps (Perception, Memory, Risk, Strategy, Execution)
- [ ] Set up Neon PostgreSQL database
- [ ] Set up Upstash Redis
- [ ] Set up Pinata IPFS account
- [ ] Set up Vercel project
- [ ] Create .env.example template
- [ ] Set up GitHub Actions for CI/CD

### Week 2: Architecture Files
- [ ] **DATABASE_SCHEMA.md** - Create detailed PostgreSQL schema (see below)
- [ ] **API_CONTRACTS.md** - Define all FastAPI endpoints (request/response formats)
- [ ] **SMART_CONTRACTS.md** - Write Solidity contracts for TST, escrow, staking
- [ ] **FRONTEND_ROUTES.md** - Define Next.js pages and components
- [ ] **ENTITY_COMMUNICATION.md** - Define Ably channel structure
- [ ] **SECURITY_CHECKLIST.md** - Security review items
- [ ] **TESTING_STRATEGY.md** - Test plans for all services

**Deliverables:**
- Empty monorepo structure set up
- All infrastructure accounts created
- Architecture documents written (referenced below)
- GitHub Actions workflows ready
- Local Docker setup for entity testing

---

## PHASE 0.5: DEVELOPER API FOUNDATION (Weeks 2-3)

### Week 2-3: REST API Infrastructure

**Backend (2 days):**
```
File: backend/routes/api_v1.py

1. API Framework Setup
   - FastAPI app with OpenAPI/Swagger
   - Rate limiting middleware (Free: 100/day, Pro: 10k/day)
   - Authentication (API key validation)
   - Error handling standardized

2. Free Tier Endpoints (Read-only)
   - GET  /v1/auth/me
   - GET  /v1/wallets
   - GET  /v1/wallets/{id}/balances
   - GET  /v1/strategies/queue
   - GET  /v1/strategies/{id}/performance
   - GET  /v1/entities/perception/signals
   - GET  /v1/entities/risk/confidence
   - GET  /v1/audit/trail

3. Database (API Keys table)
   - api_keys table: tier, rate_limit, last_used, created_at
   - Map user_id → api_key
   - Support key rotation (Pro/Enterprise)
```

**Frontend (1 day):**
```
File: frontend/pages/api-keys.tsx

1. API Key Management Dashboard
   - Generate new keys
   - Copy to clipboard
   - View usage stats
   - Revoke old keys
   - Show tier info
```

**Documentation (1 day):**
```
Files: docs/API_REFERENCE.md, docs/QUICKSTART_API.md

1. Swagger UI (auto-generated)
2. Code examples (JS, Python, cURL)
3. Authentication guide
4. Rate limiting explanation
5. Webhook setup guide (Pro tier prep)
```

**SDKs (Phase 1 Weeks 2-3):**
```
1. JavaScript/TypeScript SDK
   - File: packages/sdk-js
   - npm install @citadel/api
   - Auto-generated from OpenAPI spec

2. Python SDK
   - File: packages/sdk-python
   - pip install citadel-api
   - Auto-generated from OpenAPI spec
```

---

## PHASE 1: MVP (Weeks 3-8) - 5 Features + Developer APIs

### Feature 1: Multi-Chain Wallet Management (Week 3-4)

**Backend (Weeks 3):**
```
File: backend/services/wallet_service.py

1. HD Wallet Derivation
   - Input: master_seed (from env), user_id
   - Output: private_key, public_address
   - Standard: BIP39 (24-word), BIP44 (m/44'/60'/0'/0/[user_id])
   - Chains: BSC (same as Polygon), Tron (different encoding)

2. Wallet Creation Endpoint
   - POST /wallet/create
   - Request: { user_id: int }
   - Response: { wallet_id, address, public_key, chains: [bsc, polygon, tron] }
   - Storage: Save to users_wallets table

3. Wallet Balance Endpoint
   - GET /wallet/{wallet_id}/balances
   - Request: query params chain (bsc, polygon, tron)
   - Response: { balance: float, token_balances: [USDC, USDT, BNB, MATIC, etc.] }
   - Source: Query from chain RPC (ethers.js for EVM, web3.py for Tron)

4. Security
   - Never return private key in response
   - Private key generated on-demand, deleted after use
   - Signing always isolated (Signing Service only)
```

**Frontend (Week 4):**
```
File: frontend/pages/wallet.tsx

1. Wallet Connection
   - WalletConnect modal (user connects MetaMask)
   - Derrive TradeSynapse wallets on backend
   - Show unified dashboard

2. Wallet Display Component
   - Show all wallets (BSC, Polygon, Tron)
   - Balances in USD (price feed integrated)
   - Breakdown by token (USDC, USDT, BNB, MATIC, TST)
   - "Send" button (for basic transfers)

3. Components to Build:
   - <WalletConnect />: MetaMask connection
   - <BalanceCard />: Show single chain balance
   - <UnifiedDashboard />: Aggregate view
   - <SendModal />: Initiate transfer (placeholder for MVP)

4. Data Flow:
   - User connects → GET /wallet/create → show walances → display
```

**Database Schema (see DATABASE_SCHEMA.md):**
```sql
CREATE TABLE users_wallets (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  master_address VARCHAR(255) NOT NULL,
  bsc_address VARCHAR(255),
  polygon_address VARCHAR(255),
  tron_address VARCHAR(255),
  balance_usd FLOAT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE wallet_balances (
  id SERIAL PRIMARY KEY,
  wallet_id INT NOT NULL REFERENCES users_wallets(id),
  chain VARCHAR(50),
  token VARCHAR(50),
  balance FLOAT,
  usd_value FLOAT,
  last_updated TIMESTAMP DEFAULT NOW()
);
```

**Acceptance Criteria:**
- ✓ User can connect MetaMask
- ✓ System derives wallets for all 3 chains
- ✓ User sees unified balance view
- ✓ Balances update every 30 seconds
- ✓ No private keys exposed in API responses
- ✓ All tests passing

---

### Feature 2: Autonomous Control Plane (Week 5-6)

**Backend (Week 5):**
```
File: backend/services/perception_service.py (Fly.io service)

1. Perception Entity
   - Connects to DEX/CEX APIs
   - Publishes market data to Ably every 30 seconds
   - Data includes: prices, volumes, spreads, on-chain metrics

2. API Endpoints
   - GET /entity/perception/status - Current data freshness
   - GET /entity/perception/latest - Last tick published

3. Integration
   - Reads from: CoinGecko, Binance API, on-chain RPC
   - Publishes to: Ably channel "market.data"
   - Rate limited: 30s between ticks

File: backend/services/memory_service.py (Fly.io service)

1. Memory Entity
   - Subscribes to Ably "market.data" channel
   - Processes into patterns (every 5 minutes)
   - Stores in PostgreSQL

2. API Endpoints
   - GET /entity/memory/patterns - Last 100 ticks analyzed
   - GET /entity/memory/forecast - 5min/30min/1h forecast

File: backend/services/risk_service.py (Fly.io service)

1. Risk Entity
   - Subscribes to memory patterns
   - Applies risk constraints
   - Weights strategies (not veto)

2. API Endpoints
   - GET /entity/risk/weights - Current confidence weights
   - GET /entity/risk/constraints - Current limits

File: backend/services/strategy_service.py (Fly.io service)

1. Strategy Entity
   - Reads risk weights + patterns
   - Generates decision queue
   - Ranks by confidence

2. API Endpoints
   - GET /entity/strategy/queue - Current decisions ranked
   - POST /entity/strategy/veto - User can veto a decision (optional)

3. Decision Structure:
   {
     "decision_id": "str",
     "strategy_type": "arbitrage|lending|escrow|routing",
     "amount": float,
     "chain": "bsc|polygon|tron",
     "confidence": float (0-1),
     "expected_return": float,
     "reasoning": "str (for user explanation)"
   }

File: backend/services/execution_service.py (Fly.io service)

1. Execution Entity
   - Polls strategy queue
   - Calls Signing Service
   - Broadcasts to blockchain
   - Logs outcome

2. API Endpoints
   - GET /entity/execution/history - Completed decisions
   - GET /entity/execution/active - Currently executing
```

**Frontend (Week 6):**
```
File: frontend/pages/control-plane.tsx

1. Control Plane Dashboard
   - Show entity status (online, last update)
   - Show decision queue (ranked by confidence)
   - Real-time execution status
   - Manual pause/resume button

2. Components:
   - <EntityStatus />: Show each entity health
   - <DecisionQueue />: List ranked decisions (expandable for details)
   - <ExecutionMonitor />: Real-time tx status
   - <ControlButtons />: Pause/resume (disable entities manually)

3. Data Flow:
   - Subscribe to Ably "decisions.queue" (real-time updates)
   - Poll /entity/strategy/queue every 5 seconds
   - Show confidence scores, expected returns, reasoning

4. Interactions:
   - User can click to see decision details
   - User can click "Pause" to temporarily stop executions
   - User can click "Resume" to restart

Database:
```sql
CREATE TABLE decisions (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  strategy_type VARCHAR(50),
  amount FLOAT NOT NULL,
  chain VARCHAR(50),
  confidence FLOAT,
  expected_return FLOAT,
  reasoning TEXT,
  status VARCHAR(50) DEFAULT 'pending', -- pending, executing, completed, failed
  tx_hash VARCHAR(255),
  actual_return FLOAT,
  executed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE entity_logs (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  entity_name VARCHAR(50), -- perception, memory, risk, strategy, execution
  action TEXT,
  output TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

**Acceptance Criteria:**
- ✓ All 5 entities deployed to Fly.io
- ✓ Entities communicate via Ably (no direct calls)
- ✓ Dashboard shows real-time entity status
- ✓ Decision queue visible + ranked by confidence
- ✓ Manual pause/resume working
- ✓ All decisions logged to database
- ✓ Logging to IPFS for audit trail

---

### Feature 3: Decision Log & Audit Trail (Week 6)

**Backend:**
```
File: backend/services/audit_service.py

1. Log Every Decision
   - After execution completes (or fails)
   - Hash the decision: SHA256(decision_json + timestamp)
   - Create Merkle tree of all hashes
   - Publish root hash + all hashes to IPFS

2. IPFS Upload Structure:
   {
     "date": "2026-01-30",
     "decisions": [
       {
         "id": "dec_001",
         "entity_decisions": {
           "perception": {...},
           "memory": {...},
           "risk": {...},
           "strategy": {...},
           "execution": {...}
         },
         "outcome": "success|failed",
         "profit": 150.50,
         "timestamp": "2026-01-30T15:32:00Z"
       }
     ],
     "merkle_root": "0x...",
     "cid": "Qm..."
   }

3. Endpoints:
   - GET /audit/export - Download all decisions as JSON
   - GET /audit/hash - Get IPFS hash of decisions
   - GET /audit/verify - Verify integrity of exported data
```

**Frontend:**
```
File: frontend/pages/audit.tsx

1. Audit Trail Page
   - Timeline of all decisions (newest first)
   - Each decision expandable to show reasoning
   - Export button (JSON for tax audit)
   - IPFS hash link (immutable proof)

2. Components:
   - <DecisionTimeline />: All decisions chronological
   - <DecisionDetail />: Expand to see entity logs
   - <ExportButton />: Download JSON
   - <IPFSLink />: Link to immutable record

3. Interactions:
   - Click decision → see all entity reasoning
   - Click export → download JSON for accountant
   - Click IPFS → view immutable record
```

**Acceptance Criteria:**
- ✓ Every decision logged to database
- ✓ Weekly export to IPFS (Merkle tree)
- ✓ Audit page shows all decisions
- ✓ Export functionality working
- ✓ IPFS links immutable and verifiable

---

### Feature 4: Wallet Guardian (Week 7)

**Backend:**
```
File: backend/services/guardian_service.py

1. Anomaly Detection ML Model
   - Training data: 1000+ historical transactions
   - Features: time_of_day, amount_vs_average, destination_is_new, ip_location, etc.
   - Model: XGBoost classifier (normal vs suspicious)
   - Threshold: 70% anomaly score triggers pause

2. Detection Rules (MVP, simple):
   - Transfer at 3am-6am (off-hours): 60% anomaly
   - Transfer > 2x user's average: 50% anomaly
   - New destination address: 40% anomaly
   - VPN detected: 30% anomaly
   - Sum anomaly scores, trigger if > 70%

3. Pause Mechanism:
   - When suspicious tx detected:
     1. Stop broadcasting to blockchain
     2. Create "pending_approval" record
     3. Send 2FA challenge to user (MetaMask sign)
     4. Wait for user confirmation (5 min timeout)
     5. If approved: broadcast tx
     6. If denied: cancel tx, notify user

4. Endpoints:
   - POST /guardian/check - Pre-flight check before tx
   - GET /guardian/pending - Show pending approvals
   - POST /guardian/approve - User approves via 2FA
   - POST /guardian/deny - User rejects

Database:
```sql
CREATE TABLE guardian_checks (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  tx_hash VARCHAR(255),
  amount FLOAT,
  destination VARCHAR(255),
  anomaly_score FLOAT,
  reason TEXT,
  status VARCHAR(50) DEFAULT 'pending', -- pending, approved, denied
  created_at TIMESTAMP DEFAULT NOW(),
  approved_at TIMESTAMP
);
```

**Frontend:**
```
File: frontend/components/GuardianAlert.tsx

1. Alert Component
   - Shows when anomaly detected
   - Displays reason (off-hours, new address, etc.)
   - 2FA button (sign with MetaMask)
   - Approve/Deny buttons

2. Interactions:
   - User sees: "Unusual activity: New address, $15k transfer"
   - User clicks "Approve"
   - MetaMask 2FA prompt
   - User signs
   - Transfer proceeds

3. Styling:
   - Red/warning colors
   - Top-of-page alert (not dismissible)
   - 5 minute countdown to timeout
```

**Acceptance Criteria:**
- ✓ Anomaly detection model trained + tested
- ✓ Pause mechanism blocks suspicious txs
- ✓ 2FA confirmation working
- ✓ User alerts clear + actionable
- ✓ All detected anomalies logged

---

### Feature 5: TST Token Basics (Week 8)

**Smart Contracts (Solidity):**
```solidity
File: contracts/TST.sol

// ERC20 token with:
// - 1,000,000 total supply
// - Staking mechanism (5-12% APY)
// - Fee discount system (30-50% with staking)

contract TST is ERC20, Ownable {
  mapping(address => uint256) public stakedAmount;
  mapping(address => uint256) public stakeTimestamp;
  
  function stake(uint256 amount) external {
    // Transfer TST to staking contract
    // Record stake amount + timestamp
  }
  
  function unstake() external {
    // Release staked TST
    // Calculate rewards (5-12% APY based on duration)
    // Transfer to user
  }
  
  function getFeeDiscount(address user) external view returns (uint256) {
    // If user staked TST:
    // 10,000 TST staked → 30% discount
    // 50,000 TST staked → 50% discount
    // No stake → 0% discount
    return discount;
  }
}

File: contracts/Airdrop.sol

// Airdrop 1,000 TST to new users
contract TST_Airdrop {
  mapping(address => bool) public hasReceived;
  
  function claimAirdrop() external {
    require(!hasReceived[msg.sender], "Already claimed");
    require(total_supply_remaining > 1000, "Airdrop exhausted");
    
    // Transfer 1,000 TST to user
    // Set 30-day lockup
    // Mark as claimed
  }
}
```

**Backend:**
```
File: backend/routes/token_routes.py

1. Endpoints:
   - POST /token/claim-airdrop - Claim 1,000 TST (once per user)
   - GET /token/stake-info - Show staking rewards
   - POST /token/stake - Deposit TST to earn APY
   - POST /token/unstake - Withdraw + claim rewards
   - GET /token/fee-discount - Get user's fee discount %

2. Token Transfer:
   - After deployment, send:
     - 400k TST to Treasury address
     - 200k TST to Team vesting contract
     - 150k TST to Investor addresses
     - 150k TST to Airdrop contract (1M users max)
     - 100k TST to DEX for liquidity
```

**Frontend:**
```
File: frontend/pages/token.tsx

1. Token Page
   - Show user's TST balance
   - Show staking rewards (if any)
   - Staking form (deposit TST, see APY)
   - Unstaking form (withdraw + rewards)
   - Fee discount info (if staked)

2. Components:
   - <TokenBalance />: Show holdings
   - <StakingForm />: Deposit/unstake
   - <RewardsCalculator />: Show APY based on amount
   - <FeeDiscount />: Show current discount %

Database:
```sql
CREATE TABLE token_stakes (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  amount FLOAT NOT NULL,
  stake_timestamp TIMESTAMP DEFAULT NOW(),
  unlock_timestamp TIMESTAMP,
  reward_claimed BOOLEAN DEFAULT FALSE,
  reward_amount FLOAT
);
```

**Acceptance Criteria:**
- ✓ TST contract deployed to BSC mainnet
- ✓ Airdrop working (1,000 TST per user, once)
- ✓ Staking rewards calculated (5-12% APY)
- ✓ Fee discount applied based on stake
- ✓ User interface clean + intuitive
- ✓ Smart contract audited (or audit scheduled)

---

## PHASE 1 SUMMARY

**By end of Week 8:**
- ✓ MVP launched with 5 features
- ✓ 5 Fly.io services running (Perception, Memory, Risk, Strategy, Execution)
- ✓ Frontend deployed to Vercel
- ✓ Database operational on Neon
- ✓ Smart contracts deployed on BSC
- ✓ 100 beta users onboarded
- ✓ All decisions logged + auditable
- ✓ Wallet Guardian protecting users

---

## PHASE 2: ADVANCED FEATURES (Weeks 9-12)

### Feature 6: P2P Capital Agreements (Week 9-10)
**Complexity:** High (matching algorithm + escrow)

### Feature 7: Cross-Border Router (Week 10-11)
**Complexity:** High (multi-chain coordination)

### Feature 8: Escrow & Conditional Settlement (Week 11-12)
**Complexity:** High (smart contract logic)

### Developer API Enhancements (Phase 2, Weeks 1-4)

**Pro Tier APIs (Week 1-2):**
```
Backend: backend/routes/api_v1_pro.py

1. Write Endpoints (Pro tier)
   - POST /v1/strategies/{id}/veto
   - POST /v1/strategies/{id}/adjust-threshold
   - POST /v1/user/preferences/update
   - POST /v1/webhook/subscribe

2. Webhooks System
   - Redis pub/sub for event streaming
   - Webhook retry logic (exponential backoff)
   - Event types: strategy.executed, profit.claimed, risk.alert
   - Webhook signature verification (HMAC-SHA256)

3. API Usage Dashboard
   - Real-time request tracking
   - Cost calculator ($0.01 per 100 overage requests)
   - Billing integration (Stripe)
   - Usage analytics (requests, endpoints called, response times)
```

**Enterprise Tier APIs (Week 3-4):**
```
Backend: backend/routes/api_v1_enterprise.py

1. Custom Strategies
   - POST /v1/strategies/custom/deploy
   - Strategy validation + deployment
   - Multi-chain execution

2. White-Label Support
   - Domain mapping (yourdomain.com/api/v1)
   - Custom rate limits per endpoint
   - Private documentation

3. Data Export APIs
   - POST /v1/audit/export (full history)
   - POST /v1/analytics/custom-report
   - Compliance data in CSV/JSON

4. Admin Console
   - GET  /v1/admin/dashboard
   - GET  /v1/admin/users
   - POST /v1/api-keys/manage
   - DELETE /v1/api-keys/{id}
```

**Developer Marketplace (Week 4+):**
```
Frontend + Backend: Developer marketplace MVP

1. Marketplace Platform
   - Developers publish strategies
   - Version control, reviews, ratings
   - One-click install for users

2. Revenue Splitting
   - Smart contracts for automated payouts
   - 70% creator, 20% Citadel, 10% network
   - Monthly settlement to developer wallets

3. Developer Profiles
   - GitHub verification
   - Portfolio of published strategies
   - Reputation/rating system
```

**(Details for Phase 2 in separate PHASE2_ROADMAP.md)**

---

## TESTING STRATEGY (Throughout)

**Unit Tests:**
```
- wallet_service.py: 20 tests (derivation, signing)
- perception_service.py: 15 tests (data validation)
- memory_service.py: 25 tests (pattern recognition)
- risk_service.py: 20 tests (weighting logic)
- strategy_service.py: 30 tests (decision ranking)
- execution_service.py: 25 tests (tx broadcasting)
- guardian_service.py: 20 tests (anomaly detection)
- Total: 155+ unit tests
- Coverage: 85%+ of code
```

**Integration Tests:**
```
- Entity communication (Ably) - 10 tests
- Database integration - 15 tests
- Smart contract interaction - 20 tests
- End-to-end user flow - 10 tests
- Total: 55+ integration tests
```

**Load Testing:**
```
- 1,000 concurrent users
- 100 decisions/second
- Measure: latency, error rate, resource usage
```

**Security Testing:**
```
- OWASP Top 10 checks
- Smart contract audit (external)
- Private key exposure tests
- Authorization bypass tests
```

---

## MONITORING & OBSERVABILITY

**Dashboards:**
```
- Entity health (Datadog)
- Database performance (Neon built-in)
- API latency (Fly.io built-in)
- User activity (custom)
- Decision success rate (custom)
- Revenue tracking (custom)
```

**Alerts:**
```
- Entity down > 1 minute
- API latency > 500ms
- Decision failure rate > 5%
- Database connection pool exhausted
- Signing Service queue building up
- User funds at risk (Guardian triggered > 10x/day)
```

---

## DEPLOYMENT CHECKLIST

Before going live:

- [ ] All 155+ unit tests passing
- [ ] All 55+ integration tests passing
- [ ] Code reviewed by 2 people
- [ ] Security audit completed
- [ ] Smart contracts audited
- [ ] Database backups working
- [ ] Monitoring dashboards set up
- [ ] Runbooks written (how to recover from outages)
- [ ] Legal review completed
- [ ] Documentation complete
- [ ] 100 beta users tested
- [ ] Performance load test passed
- [ ] Incident response plan ready

---

**Document Version:** 1.0  
**Next steps:** Create DATABASE_SCHEMA.md, API_CONTRACTS.md, SMART_CONTRACTS.md
