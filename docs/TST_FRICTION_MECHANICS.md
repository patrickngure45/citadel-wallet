# TST Friction Mechanics Design

**Phase 1 Week 2 Implementation Spec**

---

## Overview

TST creates unavoidable demand through three friction points:
1. **P2P Agreement Creation** - Lock TST to secure commitment
2. **Priority Execution** - TST stake unlocks faster processing
3. **Entity Compute Access** - Advanced features require TST

---

## Friction Point 1: P2P Agreement Creation

### What It Is
Users can create P2P trading agreements with other operators (e.g., "I'll manage your $100K with these parameters").

### The Friction
Creating agreements locks TST for the agreement duration.

### Mechanics

**Tier System for P2P Creation:**

| Tier | TST Locked | Max Agreement Value | Duration Cap | Features |
|------|-----------|-------------------|--------------|----------|
| 0 | 0 | $0 | N/A | Can't create (read-only) |
| 1 | 10 | $50K | 90 days | Basic agreements |
| 2 | 50 | $500K | 180 days | Advanced terms |
| 3 | 250+ | Unlimited | Unlimited | Custom parameters |

**User Flow:**

1. User navigates to "Create P2P Agreement"
2. System shows: "Creating a $50K agreement requires 10 TST locked for 90 days"
3. User clicks "Proceed with Lock"
4. 10 TST transferred to escrow contract
5. Agreement created and live
6. TST locked until agreement expires or is terminated
7. TST automatically released when agreement ends

**Database Record:**

```
P2PAgreement {
  id: string
  creator_id: string
  counterparty_id: string
  agreement_value: Decimal
  tst_locked: Decimal (10, 50, 250+)
  locked_until: DateTime
  status: "active" | "completed" | "terminated"
  created_at: DateTime
  ...
}
```

**Key Points:**
- ✅ TST is locked, not spent (user recovers it)
- ✅ Lock duration = agreement duration (prevents gaming)
- ✅ Tier upgrade enables larger deals (not just more agreements)
- ✅ Terminating early = TST released immediately (penalty-free)

---

## Friction Point 2: Priority Execution Windows

### What It Is
All user strategies have a "cooldown" period before execution (to prevent hot-headed trades).

### The Friction
TST stake reduces or eliminates cooldowns.

### Mechanics

**Default Cooldown (No TST):**
- After strategy creation: 24-hour wait before first execution
- After trade execution: 4-hour wait before next trade
- Prevents impulsive decisions

**Tier System for Cooldown Reduction:**

| Tier | TST Stake | First Execution | Between Trades | Cost |
|------|-----------|-----------------|----------------|------|
| 0 | 0 | 24 hours | 4 hours | Free, but slow |
| 1 | 5 | 12 hours | 2 hours | Stake 5 TST (earn if strategy succeeds) |
| 2 | 25 | 1 hour | 15 min | Stake 25 TST |
| 3 | 100+ | Instant | Instant | Stake 100+ TST |

**User Flow:**

1. User creates a strategy
2. System: "Default: 24-hour wait before execution"
3. User sees: "Tier 1 ($5 TST staked): 12-hour wait"
4. User clicks "Upgrade to Tier 1"
5. 5 TST staked (locked in contract)
6. Cooldown reduced to 12 hours
7. If strategy executes successfully: TST unstakes automatically after 48 hours
8. If strategy fails: TST unstakes after 72 hours (slight penalty)

**Database Record:**

```
Strategy {
  id: string
  user_id: string
  tst_tier: 0 | 1 | 2 | 3
  tst_staked: Decimal
  last_execution: DateTime
  next_executable: DateTime (calculated based on tier)
  ...
}
```

**Key Points:**
- ✅ TST is staked temporarily (not locked permanently)
- ✅ Tier directly maps to real speed improvement (not just cosmetic)
- ✅ Unsuccessful strategies still unlock TST (no double penalty)
- ✅ Encourages serious strategists (risk-aware users)

---

## Friction Point 3: Entity Compute Access

### What It Is
Advanced AI entities run complex simulations (e.g., Monte Carlo analysis, ML-based anomaly detection).

### The Friction
Advanced entity access requires TST stake.

### Mechanics

**Entity Tiers:**

| Entity | Default | Tier 1 (5 TST) | Tier 2 (25 TST) | Tier 3 (100 TST) |
|--------|---------|---|---|---|
| **Risk** (3-min cycle) | 1x/day | 3x/day | 10x/day | Unlimited |
| **Strategy** (2-min cycle) | 1x/week | 3x/week | Daily | Unlimited |
| **Memory** (5-min cycle) | Monthly | Weekly | Daily | Real-time |
| **Custom Entities** | N/A | Limited | Full | Full + priority |

**User Flow (Strategy Designer):**

1. User wants to run custom entity configuration
2. System: "Advanced entities require compute stake"
3. Options shown:
   - Free: 1 Risk analysis per day
   - Tier 1: "Stake 5 TST → 3 analyses per day"
   - Tier 2: "Stake 25 TST → 10 analyses per day"
4. User selects Tier 1
5. 5 TST staked for 30 days
6. Increased entity access for 30 days
7. Auto-unstakes after 30 days unless renewed

**Database Record:**

```
EntityAccessTier {
  id: string
  user_id: string
  entity_type: "risk" | "strategy" | "memory" | "perception"
  tst_staked: Decimal
  tier: 1 | 2 | 3
  access_until: DateTime
  queries_remaining: Integer (resets daily)
  queries_used_today: Integer
  ...
}
```

**Key Points:**
- ✅ Compute-heavy features = higher TST requirement (fairness)
- ✅ 30-day tiers encourage longer engagement
- ✅ Usage-based (users who need more entities pay more)
- ✅ Scales with sophistication (amateur free, pro pays)

---

## Implementation Order

### Week 1: Smart Contract
```solidity
TST.sol
├── AccessControl (Tier management)
├── P2PAgreementEscrow (Lock mechanism)
├── PriorityExecutionStaking (Temporary stakes)
└── EntityComputeReserve (Allocation system)
```

### Week 2: Database Models
```
P2PAgreement (update existing)
Strategy (add tst_tier, tst_staked)
EntityAccessTier (new)
TST_LockHistory (audit trail)
TST_StakeHistory (audit trail)
```

### Week 3: API Endpoints
```
POST /api/v1/p2p/agreements/create
├── Validate TST tier
├── Lock TST in escrow
└── Create agreement

POST /api/v1/strategies/{id}/upgrade-tier
├── Validate TST balance
├── Stake TST
└── Update cooldowns

POST /api/v1/entities/access-tier/{entity}/upgrade
├── Check TST requirements
├── Stake TST
└── Grant access
```

### Week 4: UI Integration
```
No price displays anywhere
Show friction points:
- "This requires 10 TST locked"
- "Tier upgrade enables this feature"
- "Compute stake required for advanced analysis"
```

---

## Economics (Lock vs Burn)

### TST Supply Management

**Starting supply:** 1M TST (fixed, no inflation)

**Mechanisms:**
1. **P2P Locks** - TST removed from circulation during agreement
2. **Execution Stakes** - TST locked for 48-72 hours per strategy run
3. **Entity Tiers** - TST locked for 30-day periods
4. **Burns** (Future) - TST burned for irreversible actions (if needed Phase 2+)

**Result:**
- Circulating supply shrinks as usage grows
- No inflation ever
- Scarcity emerges naturally from locking, not marketing

**Example Scenario (3 months in):**

```
Month 1:
- 1M TST total supply
- 50 users, 25 TST locked in P2P agreements
- ~975K TST circulating
- Price: Not discussed yet

Month 2:
- 150 users, 500 TST locked in P2P agreements
- 200 TST in active strategy stakes
- ~800K TST circulating
- Price: Still not discussed

Month 3:
- 400 users, 2K TST locked in P2P agreements
- 500 TST in active strategy stakes
- 1K TST in entity compute tiers
- ~700K TST circulating
- Price: Natural appreciation (supply down, usage up)
- Price discussion begins ONLY if organic demand is clear
```

---

## UI Patterns (What Users See)

### Pattern 1: Friction Revealed
```
User clicks "Create Agreement"
↓
[Modal appears]
"Creating a $50K agreement requires 10 TST locked"
"Agreement duration: 90 days"
"TST will be released when agreement completes"
[Proceed] [Cancel]
```

### Pattern 2: Tier Comparison
```
User views strategy execution settings
↓
Default Tier
- 24-hour wait
- Free
[Selected]

Tier 1 (5 TST)
- 12-hour wait
- +3x faster analysis
[Upgrade]

Tier 2 (25 TST)
- 1-hour wait
- +10x faster analysis
[Upgrade]
```

### Pattern 3: Requirement Messaging
```
User tries to access advanced entity
↓
"Advanced entities require compute stake"
"Current: Free tier (1 analysis/day)"
"Next: Tier 1 (5 TST → 3 analysis/day)"
"How TST works" [help link]
[Proceed] [Cancel]
```

**Key principle:** TST requirement is *contextual* and *functional*, never promotional.

---

## Metrics to Track

**Month 1-2:**
- Total TST locked (should grow weekly)
- % of users on Tier 1+ (target: 20%)
- Average lock duration
- Re-stakes after expiry

**Month 2-3:**
- TST required for P2P agreements (increasing adoption)
- Entity tier penetration (users running advanced analyses)
- Circulating supply (should shrink from locking)
- Zero price data (we don't track this yet)

**Success Criteria:**
- 50+ TST locked in P2P agreements (not for speculation, for actual deals)
- 30%+ of active users on Tier 1+
- Weekly growth in locking (organic demand)
- No secondary market yet

---

## What This Achieves

✅ **Unavoidable Demand** - TST required to do productive things, not optional

✅ **Quality User Selection** - Only operators who need features buy/hold TST

✅ **Organic Scarcity** - Supply shrinks from locking, not artificial burns

✅ **Defensible Mechanics** - Each TST requirement solves a real problem

✅ **No Marketing Needed** - Growth is purely usage-driven

✅ **Institutional Appeal** - Serious funds see this and understand the discipline

---

## What This Prevents

❌ Price speculation (no price data to speculate on)

❌ Retail casino behavior (friction keeps tourists out)

❌ Unsustainable yield (no yield promises to break)

❌ Early hype death (quiet growth is healthier)

❌ Regulatory risk (no "investment" messaging = cleaner classification)

---

## Next Steps

1. **Freeze this spec** (no changes without explicit approval)
2. **Design smart contract** (TST as access token, not reward)
3. **Build API endpoints** (Week 2)
4. **Integrate UI** (Week 3-4)
5. **Launch to beta users only** (no public announcement yet)
6. **Monitor adoption** (measure locking, not price)
