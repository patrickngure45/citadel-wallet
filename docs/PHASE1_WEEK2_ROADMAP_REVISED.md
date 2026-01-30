# Phase 1 Week 2 Implementation Roadmap

**Updated:** January 30, 2026  
**TST Approach:** Access Token Model (not Staking Rewards)  
**Status:** Ready for implementation

---

## Week 2 Objectives

**Goal:** Implement TST access model with 3 friction points  
**Timeline:** 7 days  
**Deliverables:** Smart contract + API integration + beta testing

---

## Day 1-2: Smart Contract Development

### Tasks

1. **TST ERC20 Contract** (2 hours)
   - Fixed supply (1M TST)
   - No minting, no inflation
   - Standard ERC20 interface
   - File: `contracts/TST.sol`

2. **P2P Agreement Escrow** (4 hours)
   - Lock/unlock mechanism
   - Duration-based release
   - Early termination support
   - File: `contracts/P2PAgreementEscrow.sol`

3. **Access Tier Staking** (4 hours)
   - 30-day stake periods
   - Tier 1/2/3 levels
   - Quota allocation
   - File: `contracts/AccessTierStaking.sol`

4. **Entity Compute Reserve** (4 hours)
   - Usage-based quota system
   - Daily reset mechanism
   - Entity-to-cost mapping
   - File: `contracts/EntityComputeReserve.sol`

5. **Unit Tests** (4 hours)
   - Test locking mechanism
   - Test staking periods
   - Test quota system
   - Test edge cases

**Deliverable:** 4 smart contracts + tests on testnet

---

## Day 3: Testnet Deployment & Testing

### Tasks

1. **Deploy to BSC Testnet** (1 hour)
   - All 4 contracts
   - Verify bytecode
   - Check gas costs

2. **Internal Testing** (4 hours)
   - Lock/unlock workflow
   - Tier staking workflow
   - Quota consumption
   - Emergency unstaking

3. **Documentation** (2 hours)
   - Contract addresses
   - Gas costs
   - Deployment notes

**Deliverable:** Contracts live on testnet, ready for integration

---

## Day 4-5: Backend API Integration

### New API Endpoints

#### 1. P2P Agreement Locking

```
POST /api/v1/p2p/agreements/{agreement_id}/lock-tst

Request:
{
  "user_id": "user_123",
  "tst_amount": 10,  // 10 TST
  "duration_days": 90,
  "wallet_address": "0x..."
}

Response:
{
  "status": "locked",
  "tx_hash": "0x...",
  "tst_locked": 10,
  "locked_until": "2026-05-01T00:00:00Z",
  "agreement_id": "agreement_xyz"
}
```

**Backend Logic:**
```python
# 1. Validate user has 10 TST
# 2. Call contract: escrow.lockForAgreement()
# 3. Record in P2PAgreement model:
#    - tst_locked: 10
#    - locked_until: now + 90 days
#    - tx_hash: from blockchain
# 4. Return locked status
```

#### 2. Access Tier Upgrade

```
POST /api/v1/strategies/{strategy_id}/upgrade-tier

Request:
{
  "user_id": "user_123",
  "tier": 1,  // Tier 1 = 5 TST
  "wallet_address": "0x..."
}

Response:
{
  "status": "staked",
  "tier": 1,
  "tst_staked": 5,
  "expires_at": "2026-02-28T00:00:00Z",
  "new_cooldown": "12 hours",
  "new_limits": {
    "analyses_per_day": 3,
    "max_capital": "50000"
  }
}
```

**Backend Logic:**
```python
# 1. Validate user has 5 TST
# 2. Call contract: staking.stakeForTier(TIER_1)
# 3. Update Strategy model:
#    - tst_tier: 1
#    - tst_staked: 5
#    - tier_expires: now + 30 days
# 4. Calculate new cooldowns based on tier
# 5. Return new access levels
```

#### 3. Entity Compute Access

```
POST /api/v1/entities/{entity_id}/reserve-compute

Request:
{
  "user_id": "user_123",
  "entity": "risk",  // risk, strategy, memory
  "duration_days": 30,
  "wallet_address": "0x..."
}

Response:
{
  "status": "reserved",
  "entity": "risk",
  "tst_reserved": 5,
  "quota_per_day": 10,
  "reserved_until": "2026-02-28T00:00:00Z",
  "quota_remaining_today": 10
}
```

**Backend Logic:**
```python
# 1. Validate user has required TST
# 2. Call contract: compute.reserveForEntity(ENTITY_RISK, 30)
# 3. Create EntityAccessTier model
# 4. Set quota limits based on tier
# 5. Return access details
```

#### 4. Check TST Requirements

```
GET /api/v1/tst/requirements/{action_type}

Parameters:
  - action_type: "p2p_agreement", "tier_1", "entity_risk"

Response:
{
  "action": "p2p_agreement",
  "required_tst": 10,
  "reason": "Secures commitment for agreement duration",
  "user_has": 25,
  "user_status": "qualified",
  "tier_required": 0
}
```

**Backend Logic:**
```python
# Return TST requirement for any action
# Also show user's current balance
# Let frontend show requirements before user commits
```

#### 5. Check Current Access

```
GET /api/v1/tst/access/{user_id}

Response:
{
  "current_tier": 1,
  "tst_balance": 20,
  "active_locks": [
    {
      "type": "p2p_agreement",
      "amount": 10,
      "locked_until": "2026-05-01"
    }
  ],
  "active_stakes": [
    {
      "tier": 1,
      "amount": 5,
      "expires": "2026-02-28"
    }
  ],
  "entity_access": {
    "risk": { "quota_per_day": 10, "used_today": 3 },
    "strategy": { "quota_per_day": 5, "used_today": 1 }
  }
}
```

### File Structure

```
backend/routes/
├── tst_access.py (new)
│   ├── POST /tst/requirements/{action}
│   ├── POST /p2p/{id}/lock-tst
│   ├── POST /strategies/{id}/upgrade-tier
│   ├── POST /entities/{id}/reserve-compute
│   └── GET /tst/access/{user_id}
```

### Prisma Models (Add/Update)

```prisma
// NEW: TST Locks (P2P agreements)
model TST_Lock {
  id String @id @default(cuid())
  user_id String
  user User @relation(fields: [user_id], references: [id])
  
  agreement_id String @unique
  tst_amount Decimal
  locked_until DateTime
  tx_hash String
  released Boolean @default(false)
  
  created_at DateTime @default(now())
  released_at DateTime?
  
  @@index([user_id])
  @@index([locked_until])
}

// UPDATE: P2PAgreement
model P2PAgreement {
  // ... existing fields
  tst_locked Decimal? @default(0)
  locked_until DateTime?
  tst_tx_hash String?
}

// NEW: TST Stakes (Access tiers)
model TST_Stake {
  id String @id @default(cuid())
  user_id String
  user User @relation(fields: [user_id], references: [id])
  
  tier Int  // 1, 2, 3
  tst_amount Decimal
  expires_at DateTime
  active Boolean @default(true)
  tx_hash String
  
  created_at DateTime @default(now())
  unstaked_at DateTime?
  
  @@index([user_id])
  @@index([expires_at])
}

// NEW: Entity Compute Access
model EntityAccessTier {
  id String @id @default(cuid())
  user_id String
  user User @relation(fields: [user_id], references: [id])
  
  entity_type String  // "risk", "strategy", "memory"
  tst_reserved Decimal
  quota_per_day Int
  quota_used_today Int @default(0)
  reserved_until DateTime
  active Boolean @default(true)
  
  last_reset DateTime @default(now())
  tx_hash String
  
  created_at DateTime @default(now())
  
  @@index([user_id])
  @@index([entity_type])
  @@index([reserved_until])
}

// UPDATE: Strategy
model Strategy {
  // ... existing fields
  tst_tier Int? @default(0)  // Access tier level
  tst_staked Decimal? @default(0)
  tier_expires DateTime?
}
```

---

## Day 6: UI Integration

### UI Changes (No Price Display)

**Before:** Show "Create Agreement" button
**After:** Show with requirement

```jsx
<button disabled={!userHas10TST}>
  Create Agreement
  {!userHas10TST && <span>(requires 10 TST locked)</span>}
</button>
```

**P2P Creation Flow:**

1. User clicks "Create Agreement"
2. Modal shows: "Creating a $50K agreement requires 10 TST locked"
3. Show TST requirement, not price
4. User confirms
5. Backend calls escrow contract
6. Show: "TST locked until [date]"

**Strategy Upgrade Flow:**

1. User views cooldown: "24-hour wait before execution"
2. Shows option: "Tier 1 (5 TST) → 12-hour wait"
3. User clicks upgrade
4. Backend stakes 5 TST
5. Cooldown immediately reduced
6. Shows: "5 TST staked until [date]"

**Entity Compute Flow:**

1. User tries to run Risk analysis
2. Shows: "Advanced analysis requires Entity Compute access"
3. Shows quota: "Free: 1/day | Tier 1: 3/day (5 TST)"
4. User upgrades
5. Quota increases immediately

### Key UI Principles

✅ Show requirements contextually
✅ Never show TST price
✅ Never show price charts
✅ Never promote TST acquisition
✅ Show TST only when action needs it

---

## Day 7: Beta Testing & Documentation

### Internal Beta Test (Day 7 Morning)

Users:
- 5 internal testers
- 2 founders
- 1 advisor with crypto experience

Flow:
- Create P2P agreement (trigger TST lock)
- Upgrade strategy tier (trigger TST stake)
- Run entity analyses (trigger quota)
- Verify cooldowns reduced
- Verify quota enforced

Checklist:
- [ ] All locks working
- [ ] All stakes working
- [ ] All quotas enforced
- [ ] No errors
- [ ] No gas issues
- [ ] UI is clear

### Documentation

**For Developers:**
- Smart contract addresses (testnet)
- Contract ABIs (JSON)
- Gas costs (average per action)
- Integration examples

**For Product Team:**
- TST requirement chart (friction points)
- User flow diagrams
- Rollout plan (first 100 users)
- Metrics to monitor

**For Compliance:**
- TST narrative (frozen document)
- Mechanics design (friction model)
- No promises about yield/investment

---

## Success Criteria

✅ **Technical:**
- All contracts deployed and tested
- All API endpoints working
- Database models integrated
- Gas costs < $5 per transaction

✅ **Functional:**
- P2P locks working (users can't create agreements without TST)
- Tier upgrades working (cooldowns actually reduce)
- Entity quotas enforced (users hit limits)
- UI shows requirements clearly

✅ **Product:**
- Zero price mentions in UI
- TST requirement clear at point of use
- No marketing about TST yet
- Internal team understands narrative

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Smart contract bugs | Professional audit (Phase 1 → Phase 2) |
| Gas costs too high | Optimize, consider Layer 2 |
| Users confused by TST | Clear UI messaging + docs |
| Early speculation | No public announcement, beta users only |
| Regulatory issue | No yield promises = cleaner classification |

---

## Weekly Metrics (Start Collecting)

**By end of Week 2:**

- TST locks: >0 (internal testing)
- TST stakes: >0 (internal testing)
- API response times: <100ms
- Zero errors in logs
- Gas costs per action: track

**By Week 4:**

- 10+ active users
- >50 TST locked
- >20 TST staked
- Tier 1+ adoption: >30% of users

---

## Next Phase (Week 3-4)

### Week 3: Expand to Beta Users
- Invite 50 early operators
- Monitor adoption
- Collect feedback
- Refine UI based on feedback

### Week 4: Strategy Management Integration
- Connect TST tiers to strategy features
- Build strategy CRUD endpoints
- Enable veto/approve flow
- Increase tier adoption

### Week 5: 5-Entity System
- Add entity decision flow
- Integrate entity approval to TST requirements
- Set up Ably messaging
- Begin entity service implementation

---

## Rollout Plan (Critical)

**Phase 1 Week 2-3: Internal Only**
- No external announcement
- Beta testers only
- Validate mechanics

**Phase 1 Week 4-5: Closed Beta**
- Invite 100 operators
- Monitor adoption
- Collect feedback

**Phase 1 Week 6+: Soft Public**
- Documentation published
- Organic discovery
- No marketing push

**Phase 2+: Selective Exposure**
- Technical blog posts
- Conference talks
- Ecosystem partnerships
- Still no hype marketing

---

## Decision Checkpoint

**Before coding starts:**

- [ ] Team agrees: TST is access token, not investment
- [ ] Narrative frozen (TST_NARRATIVE_FROZEN.md)
- [ ] Mechanics approved (TST_FRICTION_MECHANICS.md)
- [ ] No yield promises anywhere
- [ ] No price discussion planned
- [ ] Smart contract spec reviewed

---

## Code Review Checklist

Every PR touching TST must verify:

- [ ] No staking rewards anywhere
- [ ] No yield calculations
- [ ] No inflation mechanics
- [ ] No "earn TST" language
- [ ] TST requirement is functional, not promotional
- [ ] UI shows friction (requirement), not opportunity

---

## Go/No-Go Decision

**Go if:**
- ✅ Smart contracts pass internal audit
- ✅ Team committed to frozen narrative
- ✅ No yield mechanisms anywhere
- ✅ UI shows requirements (not promotions)
- ✅ Beta test successful

**No-Go if:**
- ❌ Any yield mechanism discovered
- ❌ Team pressure to "make TST valuable"
- ❌ Marketing wants to promote TST
- ❌ Regulatory concerns about classification

---

**Status:** READY TO IMPLEMENT ✅

Next action: Approve this roadmap, then start smart contract development on Day 1.
