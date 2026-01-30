# Database Schema
## Citadel: PostgreSQL 16 Design

**Brand:** Citadel | **Protocol:** TradeSynapse  
**Database:** Neon PostgreSQL 16  
**Status:** Phase 0 Week 2  
**Last Updated:** January 30, 2026

---

## Overview

**Tables: 13**  
**Relationships: Multi-tenant, user-segregated**  
**Constraints: Comprehensive (foreign keys, checks, uniqueness)**  
**Indexes: Strategic (performance optimized)**

---

## 1. USERS TABLE

**Purpose:** Core user authentication & profile

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  password_hash VARCHAR(255) NOT NULL,
  username VARCHAR(50) UNIQUE,
  
  -- Profile
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  avatar_url VARCHAR(500),
  bio TEXT,
  
  -- Settings
  theme VARCHAR(10) CHECK (theme IN ('dark', 'light')) DEFAULT 'dark',
  language VARCHAR(10) DEFAULT 'en',
  timezone VARCHAR(50) DEFAULT 'UTC',
  
  -- Guardian (MetaMask) Settings
  guardian_address VARCHAR(42), -- MetaMask wallet address
  guardian_verified BOOLEAN DEFAULT FALSE,
  guardian_verified_at TIMESTAMP,
  
  -- Airdrop & Loyalty
  airdrop_eligible BOOLEAN DEFAULT TRUE,
  airdrop_claimed BOOLEAN DEFAULT FALSE,
  airdrop_claimed_at TIMESTAMP,
  tst_airdrop_amount DECIMAL(10, 2) DEFAULT 1000.00,
  
  -- Account Status
  status VARCHAR(20) CHECK (status IN ('active', 'suspended', 'deleted')) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  -- Compliance
  kyc_status VARCHAR(20) CHECK (kyc_status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
  kyc_verified_at TIMESTAMP,
  
  CONSTRAINT valid_email CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_kyc_status ON users(kyc_status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

---

## 2. WALLETS TABLE

**Purpose:** User's HD wallet information & balances

```sql
CREATE TABLE wallets (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Wallet Info
  wallet_type VARCHAR(20) CHECK (wallet_type IN ('personal', 'escrow', 'risk_vault', 'liquidity_pool', 'hot_wallet')) DEFAULT 'personal',
  chain VARCHAR(20) CHECK (chain IN ('bsc', 'polygon', 'tron')) NOT NULL,
  
  -- Addresses
  public_address VARCHAR(120) UNIQUE NOT NULL, -- 42 chars (EVM) or longer (Tron)
  derivation_path VARCHAR(100), -- m/44'/60'/0'/0/[user_id] or similar
  
  -- Balances (stored as denormalized cache, source of truth on-chain)
  balance_usd DECIMAL(20, 2) DEFAULT 0,
  balance_native DECIMAL(30, 18) DEFAULT 0, -- BNB, MATIC, TRX
  balance_usdt DECIMAL(20, 2) DEFAULT 0,
  balance_usdc DECIMAL(20, 2) DEFAULT 0,
  balance_tst DECIMAL(20, 2) DEFAULT 0,
  
  -- Metadata
  label VARCHAR(100), -- "Main Wallet", "Escrow for Strategy X"
  is_primary BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Tracking
  last_balance_sync TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE (user_id, chain, wallet_type)
);

CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_wallets_chain ON wallets(chain);
CREATE INDEX idx_wallets_public_address ON wallets(public_address);
```

---

## 3. TRANSACTIONS TABLE

**Purpose:** Track all on-chain transactions

```sql
CREATE TABLE transactions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  wallet_id BIGINT NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
  
  -- Transaction Details
  tx_hash VARCHAR(150) UNIQUE NOT NULL,
  chain VARCHAR(20) NOT NULL,
  from_address VARCHAR(120) NOT NULL,
  to_address VARCHAR(120) NOT NULL,
  
  -- Amount & Token
  amount DECIMAL(30, 18) NOT NULL,
  token VARCHAR(50) DEFAULT 'USDT', -- USDT, USDC, BNB, etc.
  value_usd DECIMAL(20, 2),
  
  -- Status
  status VARCHAR(20) CHECK (status IN ('pending', 'confirmed', 'failed', 'cancelled')) DEFAULT 'pending',
  confirmations INT DEFAULT 0,
  tx_index INT, -- Position in block
  
  -- Type
  tx_type VARCHAR(30) CHECK (tx_type IN ('deposit', 'withdrawal', 'strategy_execution', 'profit_claim', 'p2p_transfer', 'escrow_lock', 'escrow_release')) NOT NULL,
  
  -- References
  strategy_id BIGINT REFERENCES strategies(id) ON DELETE SET NULL,
  agreement_id BIGINT REFERENCES p2p_agreements(id) ON DELETE SET NULL,
  
  -- Metadata
  gas_used DECIMAL(20, 2),
  gas_price DECIMAL(20, 2),
  block_number BIGINT,
  block_timestamp TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_tx_hash ON transactions(tx_hash);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
```

---

## 4. STRATEGIES TABLE

**Purpose:** User's deployed trading strategies

```sql
CREATE TABLE strategies (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Strategy Info
  name VARCHAR(100) NOT NULL,
  description TEXT,
  strategy_type VARCHAR(30) CHECK (strategy_type IN ('ml_momentum', 'arbitrage', 'conservative', 'aggressive', 'custom')) DEFAULT 'ml_momentum',
  
  -- Configuration
  chain VARCHAR(20) NOT NULL,
  allocated_capital DECIMAL(20, 2) NOT NULL,
  min_trade_size DECIMAL(20, 2) DEFAULT 10,
  max_trade_size DECIMAL(20, 2),
  
  -- Risk Settings
  risk_tolerance VARCHAR(20) CHECK (risk_tolerance IN ('low', 'medium', 'high')) DEFAULT 'medium',
  max_drawdown DECIMAL(5, 2) DEFAULT 20.00, -- Percentage
  stop_loss DECIMAL(5, 2), -- Percentage
  
  -- Execution
  is_active BOOLEAN DEFAULT FALSE,
  auto_rebalance BOOLEAN DEFAULT TRUE,
  rebalance_frequency VARCHAR(20) DEFAULT 'weekly', -- daily, weekly, monthly
  
  -- Performance (denormalized)
  total_trades INT DEFAULT 0,
  wins INT DEFAULT 0,
  losses INT DEFAULT 0,
  total_profit DECIMAL(20, 2) DEFAULT 0,
  roi DECIMAL(8, 2) DEFAULT 0, -- Percentage
  
  -- Tracking
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  started_at TIMESTAMP,
  paused_at TIMESTAMP,
  stopped_at TIMESTAMP,
  
  CONSTRAINT positive_capital CHECK (allocated_capital > 0)
);

CREATE INDEX idx_strategies_user_id ON strategies(user_id);
CREATE INDEX idx_strategies_is_active ON strategies(is_active);
CREATE INDEX idx_strategies_created_at ON strategies(created_at);
```

---

## 5. STRATEGY_DECISIONS TABLE

**Purpose:** Record each decision made by TradeSynapse entity system

```sql
CREATE TABLE strategy_decisions (
  id BIGSERIAL PRIMARY KEY,
  strategy_id BIGINT NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
  
  -- Decision Source (which entity)
  entity_source VARCHAR(30) CHECK (entity_source IN ('perception', 'memory', 'risk', 'strategy', 'execution')) NOT NULL,
  
  -- Decision Details
  decision_type VARCHAR(30) CHECK (decision_type IN ('buy', 'sell', 'hold', 'rebalance', 'veto')) NOT NULL,
  
  -- Market Context
  market_signal JSONB, -- Perception entity's signal
  confidence_score DECIMAL(5, 2), -- Risk entity's confidence (0-100)
  predicted_return DECIMAL(8, 2), -- Expected % return
  
  -- Execution
  token_pair VARCHAR(30), -- ETH/USDT, BNB/USDT, etc.
  amount DECIMAL(30, 18),
  proposed_price DECIMAL(20, 2),
  
  -- Status
  status VARCHAR(20) CHECK (status IN ('pending', 'approved', 'executed', 'vetoed', 'failed')) DEFAULT 'pending',
  executed_price DECIMAL(20, 2),
  executed_amount DECIMAL(30, 18),
  
  -- Guardian Interaction
  guardian_approval_required BOOLEAN DEFAULT FALSE,
  guardian_approved BOOLEAN,
  guardian_approved_at TIMESTAMP,
  guardian_reason TEXT,
  
  -- Veto Record
  is_vetoed BOOLEAN DEFAULT FALSE,
  veto_reason TEXT,
  vetoed_by_user BOOLEAN DEFAULT FALSE, -- TRUE if user vetoed, FALSE if system vetoed
  
  -- Tracking
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  executed_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategy_decisions_strategy_id ON strategy_decisions(strategy_id);
CREATE INDEX idx_strategy_decisions_status ON strategy_decisions(status);
CREATE INDEX idx_strategy_decisions_created_at ON strategy_decisions(created_at);
```

---

## 6. ENTITY_LOGS TABLE

**Purpose:** Audit trail for all 5 entity system activities

```sql
CREATE TABLE entity_logs (
  id BIGSERIAL PRIMARY KEY,
  strategy_id BIGINT REFERENCES strategies(id) ON DELETE CASCADE,
  
  -- Entity Info
  entity_name VARCHAR(30) CHECK (entity_name IN ('perception', 'memory', 'risk', 'strategy', 'execution')) NOT NULL,
  cycle_number INT, -- Which cycle (tick) of entity ran
  
  -- Activity
  activity_type VARCHAR(50), -- 'signal_detected', 'pattern_learned', 'confidence_calculated', 'decision_ranked', 'tx_broadcasted'
  
  -- Data
  input_data JSONB,
  output_data JSONB,
  processing_time_ms INT,
  
  -- Error Handling
  error_message TEXT,
  is_error BOOLEAN DEFAULT FALSE,
  
  -- Timing
  run_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entity_logs_strategy_id ON entity_logs(strategy_id);
CREATE INDEX idx_entity_logs_entity_name ON entity_logs(entity_name);
CREATE INDEX idx_entity_logs_created_at ON entity_logs(created_at);
```

---

## 7. GUARDIAN_CHECKS TABLE

**Purpose:** Track all guardian (MetaMask) approvals & alerts

```sql
CREATE TABLE guardian_checks (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Alert Type
  alert_type VARCHAR(50) CHECK (alert_type IN ('unusual_time', 'new_address', 'large_amount', 'vpn_detected', 'rapid_transactions', 'high_risk_strategy', 'custom')) NOT NULL,
  
  -- Context
  description TEXT NOT NULL,
  risk_score DECIMAL(5, 2), -- 0-100
  
  -- Detection Details
  detected_at TIMESTAMP NOT NULL,
  context_data JSONB, -- Transaction details, location, etc.
  
  -- User Action Required
  requires_approval BOOLEAN DEFAULT TRUE,
  approval_required_until TIMESTAMP,
  
  -- Resolution
  status VARCHAR(20) CHECK (status IN ('pending', 'approved', 'rejected', 'expired')) DEFAULT 'pending',
  user_action VARCHAR(20) CHECK (user_action IN ('approve', 'reject', 'block')),
  user_action_at TIMESTAMP,
  
  -- Cost
  guardian_fee DECIMAL(10, 2) DEFAULT 0.50, -- Usually $0.50 per check
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_guardian_checks_user_id ON guardian_checks(user_id);
CREATE INDEX idx_guardian_checks_status ON guardian_checks(status);
CREATE INDEX idx_guardian_checks_alert_type ON guardian_checks(alert_type);
```

---

## 8. TST_STAKES TABLE

**Purpose:** Track TST token staking (8% APY)

```sql
CREATE TABLE tst_stakes (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  wallet_id BIGINT NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
  
  -- Stake Info
  amount DECIMAL(20, 2) NOT NULL,
  apy_percentage DECIMAL(5, 2) DEFAULT 8.00,
  
  -- Timing
  staked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  lock_until TIMESTAMP, -- When they can unstake
  
  -- Rewards
  total_rewards_earned DECIMAL(20, 2) DEFAULT 0,
  last_reward_claimed TIMESTAMP,
  next_reward_date TIMESTAMP,
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  unstaked_at TIMESTAMP,
  
  CONSTRAINT positive_amount CHECK (amount > 0)
);

CREATE INDEX idx_tst_stakes_user_id ON tst_stakes(user_id);
CREATE INDEX idx_tst_stakes_is_active ON tst_stakes(is_active);
```

---

## 9. P2P_AGREEMENTS TABLE

**Purpose:** Peer-to-peer capital lending agreements

```sql
CREATE TABLE p2p_agreements (
  id BIGSERIAL PRIMARY KEY,
  
  -- Parties
  lender_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  borrower_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  
  -- Agreement Terms
  principal_amount DECIMAL(20, 2) NOT NULL,
  interest_rate DECIMAL(5, 2) NOT NULL, -- Percentage
  duration_days INT NOT NULL,
  token VARCHAR(20) DEFAULT 'USDT',
  
  -- Escrow
  escrow_address VARCHAR(120), -- Multi-sig escrow wallet
  escrow_tx_hash VARCHAR(150),
  
  -- Status
  status VARCHAR(20) CHECK (status IN ('pending', 'active', 'completed', 'disputed', 'cancelled')) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  funded_at TIMESTAMP,
  maturity_date TIMESTAMP,
  settled_at TIMESTAMP,
  
  -- Repayment
  repayment_amount DECIMAL(20, 2), -- Principal + Interest
  repay_tx_hash VARCHAR(150),
  
  CONSTRAINT valid_interest CHECK (interest_rate >= 0 AND interest_rate <= 50),
  CONSTRAINT valid_duration CHECK (duration_days > 0)
);

CREATE INDEX idx_p2p_agreements_lender_id ON p2p_agreements(lender_id);
CREATE INDEX idx_p2p_agreements_borrower_id ON p2p_agreements(borrower_id);
CREATE INDEX idx_p2p_agreements_status ON p2p_agreements(status);
```

---

## 10. API_KEYS TABLE

**Purpose:** Developer API authentication & rate limiting

```sql
CREATE TABLE api_keys (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Key Info
  name VARCHAR(100),
  key_hash VARCHAR(255) UNIQUE NOT NULL, -- bcrypt hashed
  key_preview VARCHAR(20), -- Last 4 chars: ...ABCD
  
  -- Tier
  tier VARCHAR(20) CHECK (tier IN ('free', 'pro', 'enterprise')) DEFAULT 'free',
  rate_limit_per_day INT, -- 100 for free, 10000 for pro, unlimited for enterprise
  rate_limit_per_second INT, -- 1 for free, 100 for pro, unlimited for enterprise
  
  -- Permissions (scope)
  permissions TEXT[] DEFAULT ARRAY['read:wallets', 'read:strategies'], -- Can add write: and admin: scopes
  
  -- Usage Tracking
  total_requests INT DEFAULT 0,
  requests_today INT DEFAULT 0,
  last_used_at TIMESTAMP,
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  revoked_at TIMESTAMP
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_tier ON api_keys(tier);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
```

---

## 11. PERFORMANCE_METRICS TABLE

**Purpose:** Store daily/monthly performance snapshots

```sql
CREATE TABLE performance_metrics (
  id BIGSERIAL PRIMARY KEY,
  strategy_id BIGINT NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
  
  -- Period
  period_date DATE NOT NULL,
  period_type VARCHAR(10) CHECK (period_type IN ('daily', 'weekly', 'monthly')) DEFAULT 'daily',
  
  -- Metrics
  opening_balance DECIMAL(20, 2),
  closing_balance DECIMAL(20, 2),
  daily_profit DECIMAL(20, 2),
  daily_roi DECIMAL(8, 2), -- Percentage
  cumulative_roi DECIMAL(8, 2),
  
  -- Trading Activity
  trades_executed INT DEFAULT 0,
  winning_trades INT DEFAULT 0,
  losing_trades INT DEFAULT 0,
  win_rate DECIMAL(5, 2), -- Percentage
  
  -- Risk Metrics
  max_drawdown DECIMAL(5, 2),
  volatility DECIMAL(5, 2),
  sharpe_ratio DECIMAL(8, 2),
  
  UNIQUE (strategy_id, period_date, period_type)
);

CREATE INDEX idx_performance_metrics_strategy_id ON performance_metrics(strategy_id);
CREATE INDEX idx_performance_metrics_period_date ON performance_metrics(period_date);
```

---

## 12. AUDIT_TRAIL TABLE

**Purpose:** Immutable compliance & regulatory audit log

```sql
CREATE TABLE audit_trail (
  id BIGSERIAL PRIMARY KEY,
  
  -- User & Action
  user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  action_type VARCHAR(50) NOT NULL, -- 'strategy_created', 'funds_withdrawn', 'decision_vetoed', etc.
  
  -- Context
  entity_type VARCHAR(50), -- 'strategy', 'wallet', 'agreement'
  entity_id BIGINT,
  
  -- Details
  description TEXT,
  changes JSONB, -- Before/after values
  
  -- IP & Device
  ip_address VARCHAR(45),
  user_agent TEXT,
  
  -- Timestamp (immutable)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT immutable_timestamp CHECK (created_at = CURRENT_TIMESTAMP)
);

CREATE INDEX idx_audit_trail_user_id ON audit_trail(user_id);
CREATE INDEX idx_audit_trail_action_type ON audit_trail(action_type);
CREATE INDEX idx_audit_trail_created_at ON audit_trail(created_at);
```

---

## 13. FEATURE_FLAGS TABLE

**Purpose:** Toggle features on/off per user

```sql
CREATE TABLE feature_flags (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  
  -- Flag Info
  flag_name VARCHAR(100) NOT NULL,
  flag_value BOOLEAN DEFAULT TRUE,
  
  -- Metadata
  description TEXT,
  enabled_at TIMESTAMP,
  disabled_at TIMESTAMP,
  
  UNIQUE (user_id, flag_name)
);

CREATE INDEX idx_feature_flags_user_id ON feature_flags(user_id);
CREATE INDEX idx_feature_flags_flag_name ON feature_flags(flag_name);
```

---

## Key Relationships

```
users
  ├── 1:N wallets
  ├── 1:N strategies
  │   ├── 1:N strategy_decisions
  │   ├── 1:N entity_logs
  │   └── 1:N performance_metrics
  ├── 1:N transactions
  ├── 1:N guardian_checks
  ├── 1:N tst_stakes
  ├── 1:N p2p_agreements (as lender or borrower)
  ├── 1:N api_keys
  └── 1:N audit_trail

transactions
  ├── strategy_id (nullable)
  └── agreement_id (nullable)
```

---

## Sample Queries

### Get user's current balances
```sql
SELECT 
  w.chain,
  w.balance_usd,
  w.balance_usdt,
  w.balance_tst
FROM wallets w
WHERE w.user_id = $1 AND w.is_active = TRUE;
```

### Get strategy performance (last 30 days)
```sql
SELECT 
  pm.period_date,
  pm.daily_profit,
  pm.daily_roi,
  pm.trades_executed,
  pm.win_rate
FROM performance_metrics pm
WHERE pm.strategy_id = $1 
  AND pm.period_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY pm.period_date DESC;
```

### Get pending guardian checks
```sql
SELECT 
  id,
  alert_type,
  risk_score,
  detected_at,
  approval_required_until
FROM guardian_checks
WHERE user_id = $1 AND status = 'pending'
ORDER BY risk_score DESC;
```

### Calculate user's total staked TST
```sql
SELECT 
  SUM(amount) as total_staked,
  SUM(total_rewards_earned) as rewards_earned
FROM tst_stakes
WHERE user_id = $1 AND is_active = TRUE;
```

### Get user's P2P agreements (as lender)
```sql
SELECT 
  id,
  borrower_id,
  principal_amount,
  interest_rate,
  status,
  maturity_date
FROM p2p_agreements
WHERE lender_id = $1
ORDER BY created_at DESC;
```

### Audit trail for user actions (last 7 days)
```sql
SELECT 
  action_type,
  entity_type,
  description,
  created_at
FROM audit_trail
WHERE user_id = $1 AND created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC;
```

---

## Migration Strategy

### Phase 1: Initial Schema
```bash
# Create all tables
psql -d citadel_prod -f migrations/001_initial_schema.sql

# Add indexes
psql -d citadel_prod -f migrations/002_add_indexes.sql

# Add constraints
psql -d citadel_prod -f migrations/003_add_constraints.sql
```

### Phase 2: Seeding
```bash
# Create test data
psql -d citadel_prod -f migrations/004_seed_data.sql
```

---

## Performance Considerations

### Denormalization (Performance Optimization)
- `wallets.balance_*` — Cached from chain (synced every 5 min)
- `strategies.total_profit, roi, wins, losses` — Computed from decisions
- `performance_metrics.*` — Snapshots computed daily

### Refresh Strategy
```
Walances:       Every 5 minutes (Redis cache + DB)
Strategy Metrics: Every 1 hour (batch job)
Performance:     Daily at 2 AM UTC
```

### Indexes
- Composite indexes on frequently filtered columns
- Partial indexes for active records only
- BRIN indexes on large timestamp columns

---

## Backup & Recovery

**Daily backups:** Automated via Neon (point-in-time recovery up to 7 days)  
**Weekly archive:** Export to S3 for compliance  
**Test restoration:** Monthly DR drill

---

**Status:** Complete  
**Next:** API_CONTRACTS.md (endpoint specifications)
