// Smart Contract Deployment and Integration Guide
// This document explains how to deploy and integrate the TST smart contracts

## Quick Reference

### Smart Contracts Overview

#### 1. TST.sol (ERC20 Fixed Supply)
- **Purpose:** Fixed 1M token supply, no inflation, access control only
- **Key Features:**
  - Fixed supply (1,000,000 * 10^18)
  - No minting capability
  - Non-transferable (blocks transfer, transferFrom, approve)
  - Tracks locked and staked balances
  - No yield mechanisms

**Key Functions:**
- `recordLock(amount, lockId)` - Record TST locked for P2P agreement
- `releaseLock(amount, lockId)` - Release locked TST
- `recordStake(amount, tier)` - Record TST staked for tier access
- `recordUnstake(amount)` - Release staked TST
- `getAvailableBalance(account)` - Get unlocked, unstaked balance
- `hasAvailableBalance(account, amount)` - Verify balance requirement

#### 2. P2PAgreementEscrow.sol
- **Purpose:** Lock TST for P2P agreement duration
- **Duration:** User-defined (agreement duration)
- **Release:** Automatic after expiry or manual early termination

**Key Functions:**
- `lockForAgreement(amount, duration, agreementId)` - Create lock
- `releaseAfterExpiry(lockId)` - Release after agreement ends
- `earlyTerminate(lockId)` - Early termination (no penalties)
- `isLocked(lockId)` - Check if lock still active

**Lock Tiers:**
- Tier 0: Cannot create (0 TST)
- Tier 1: 10 TST locked → $50K max agreement
- Tier 2: 50 TST locked → $500K max agreement  
- Tier 3: 250+ TST locked → Unlimited

#### 3. AccessTierStaking.sol
- **Purpose:** Stake TST for 30-day tier access
- **Duration:** Fixed 30 days (no perpetual)
- **Yield:** None (full TST returned after 30 days)

**Key Functions:**
- `stakeForTier(tier)` - Create 30-day stake
- `unstake(stakeId)` - Unstake after 30 days
- `hasActiveTier(user, tier)` - Check if tier active
- `getHighestActiveTier(user)` - Get highest active tier

**Tier Requirements:**
- Tier 1: 5 TST → 3x/day entity analysis, 12-hour wait
- Tier 2: 25 TST → 10x/day entity analysis, 1-hour wait
- Tier 3: 100 TST → Unlimited, instant execution

#### 4. EntityComputeReserve.sol
- **Purpose:** Usage-based quotas for entity access
- **Reset:** Daily reset at 00:00 UTC
- **Quotas:** Tier-dependent allocation

**Key Functions:**
- `reserveForEntity(entity)` - Reserve for entity type
- `getQuotaRemaining(user, entity, tier)` - Check available quota
- `consumeQuota(user, entity, tier, amount)` - Consume quota (backend)
- `endReservation(reservationId)` - End reservation

**Entity Quotas (daily):**
- ENTITY_RISK (1):
  - Tier 0: 1x/day
  - Tier 1: 3x/day (5 TST)
  - Tier 2: 10x/day (25 TST)
  - Tier 3: Unlimited (100 TST)

- ENTITY_STRATEGY (2):
  - Tier 0: 4x/day (~1x/week)
  - Tier 1: 12x/day (~3x/week, 5 TST)
  - Tier 2: 28x/day (daily, 25 TST)
  - Tier 3: Unlimited (100 TST)

- ENTITY_MEMORY (3):
  - Tier 0: 2x/day (~1x/month)
  - Tier 1: 7x/day (~1x/week, 5 TST)
  - Tier 2: 28x/day (daily, 25 TST)
  - Tier 3: Unlimited (100 TST)

### Deployment on BSC Testnet

#### 1. Setup Environment
```bash
# Create .env file with:
BSC_TESTNET_RPC_URL=https://data-seed-prebsc-1-1.binance.org:8545
PRIVATE_KEY=<your_private_key>
```

#### 2. Deployment Steps
```bash
# Using Hardhat (if compilation issues resolved):
npx hardhat run scripts/deploy.js --network bscTestnet

# Alternative: Using Remix or direct solc compilation
solc --optimize --bin --abi TST.sol -o build/
```

#### 3. Deployment Order
1. Deploy TST.sol
2. Deploy P2PAgreementEscrow.sol (pass TST address)
3. Deploy AccessTierStaking.sol (pass TST address)
4. Deploy EntityComputeReserve.sol (pass TST address)

#### 4. Contract Addresses (After Deployment)
```
TST:                    0x[...]
P2PAgreementEscrow:     0x[...]
AccessTierStaking:      0x[...]
EntityComputeReserve:   0x[...]
```

### API Integration (FastAPI)

#### New Prisma Models

```prisma
model TST_Lock {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation(fields: [userId], references: [id])
  agreementId     String
  amount          BigInt   // Wei
  lockedUntil     DateTime
  released        Boolean  @default(false)
  contractLockId  String   // bytes32 from contract
  txHash          String?
  createdAt       DateTime @default(now())
  releasedAt      DateTime?

  @@index([userId])
  @@index([agreementId])
}

model TST_Stake {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation(fields: [userId], references: [id])
  tier            Int      // 1, 2, or 3
  amount          BigInt   // Wei (5, 25, or 100 TST)
  stakedAt        DateTime
  expiresAt       DateTime
  active          Boolean  @default(true)
  contractStakeId String   // bytes32 from contract
  txHash          String?
  createdAt       DateTime @default(now())
  unstakedAt      DateTime?

  @@index([userId])
  @@index([active])
}

model EntityAccessTier {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation(fields: [userId], references: [id])
  entityType      Int      // 1=Risk, 2=Strategy, 3=Memory
  tstReserved     BigInt   // Wei
  quotaPerDay     Int
  quotaUsedToday  Int      @default(0)
  lastResetTime   DateTime @default(now())
  contractResId   String?  // bytes32 from contract
  createdAt       DateTime @default(now())

  @@unique([userId, entityType])
  @@index([userId])
}
```

#### API Endpoints

```python
# POST /api/v1/p2p/{agreement_id}/lock-tst
# Lock TST for P2P agreement
{
  "amount": 10,           # TST amount
  "duration": 7776000     # seconds (90 days)
}
Response: {
  "lock_id": "0x...",
  "tx_hash": "0x...",
  "locked_until": "2026-04-30T...",
  "status": "locked"
}

# POST /api/v1/strategies/{strategy_id}/upgrade-tier
# Stake TST for tier access
{
  "tier": 2  # 1, 2, or 3
}
Response: {
  "stake_id": "0x...",
  "tx_hash": "0x...",
  "tier": 2,
  "expires_at": "2026-02-29T...",
  "benefits": {
    "entity_analysis": "10x/day",
    "execution_wait": "1 hour",
    "priority": "high"
  }
}

# POST /api/v1/entities/{entity_id}/reserve-compute
# Reserve entity access
{
  "entity_type": 1  # 1=Risk, 2=Strategy, 3=Memory
}
Response: {
  "reservation_id": "0x...",
  "entity_type": 1,
  "quota_today": 10,
  "expires_at": "2026-02-29T..."
}

# GET /api/v1/tst/requirements/{action}
# Show TST requirements
Response: {
  "action": "create_p2p_agreement",
  "tier_required": 1,
  "tst_locked": 10,
  "max_agreement_value": "$50,000"
}

# GET /api/v1/tst/access/{user_id}
# Check current TST access
Response: {
  "current_tier": 1,
  "tst_staked": "5000000000000000000",  # 5 TST in Wei
  "tier_expires": "2026-02-29T...",
  "locks": [
    {
      "lock_id": "0x...",
      "amount": "10000000000000000000",
      "agreement_id": "agr_123",
      "released": false,
      "expires": "2026-04-01T..."
    }
  ],
  "entity_quotas": {
    "risk": { "available": 8, "total": 10, "reset_at": "2026-01-31T00:00:00Z" },
    "strategy": { "available": 9, "total": 10, "reset_at": "2026-01-31T00:00:00Z" },
    "memory": { "available": 10, "total": 10, "reset_at": "2026-01-31T00:00:00Z" }
  }
}
```

### Implementation Checklist

#### Day 1-2: Smart Contracts
- [ ] TST.sol deployed and tested
- [ ] P2PAgreementEscrow.sol deployed and tested
- [ ] AccessTierStaking.sol deployed and tested
- [ ] EntityComputeReserve.sol deployed and tested
- [ ] All unit tests passing
- [ ] ABIs exported for frontend

#### Day 3: Testnet Deployment
- [ ] Contracts deployed to BSC testnet
- [ ] Contract addresses documented
- [ ] Testnet verification complete
- [ ] Gas cost analysis (<$5 per action)

#### Days 4-5: Backend Integration
- [ ] Prisma models created
- [ ] 5 API endpoints implemented
- [ ] Web3 integration (ethers.js)
- [ ] Tier logic enforced server-side
- [ ] Quota system working

#### Day 6: UI Integration
- [ ] TST requirements shown contextually
- [ ] No price displays anywhere
- [ ] Tier upgrade UI
- [ ] Lock/stake status display
- [ ] Quota remaining indicator

#### Day 7: Beta Testing
- [ ] 7 internal testers onboarded
- [ ] All flows tested end-to-end
- [ ] Documentation complete
- [ ] ABIs and integration guide ready
- [ ] Go/no-go decision made

### Critical Red Lines

🛑 **Stop Immediately If You See:**
1. Any "yield" language anywhere
2. Transfer enabled on TST contract
3. Discussion of "early opportunity"
4. Price predictions or targets
5. Minting capability in TST.sol
6. Perpetual staking (vs 30-day fixed)
7. Any governance token features

### Testing Commands

```bash
# Compile contracts
npx hardhat compile

# Run all tests
npx hardhat test

# Run specific test file
npx hardhat test test/TST.test.js

# Run test with specific pattern
npx hardhat test --grep "Should lock TST"

# Compile and deploy to local network
npx hardhat run scripts/deploy.js

# Deploy to testnet
npx hardhat run scripts/deploy.js --network bscTestnet
```

### Gas Estimation (BSC)

- TST deployment: ~2.5M gas
- Escrow deployment: ~1.8M gas
- Staking deployment: ~1.5M gas
- Compute deployment: ~2M gas
- Lock operation: ~80k gas
- Stake operation: ~90k gas
- Consume quota: ~70k gas

**Total deployment cost at 3 gwei:** ~$50-80 USD

