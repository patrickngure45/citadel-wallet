# TST Strategy Revision: From Staking to Access Control

**Date:** January 30, 2026  
**Trigger:** Fundamental insight about token growth  
**Impact:** Complete redesign of TST mechanics  
**Status:** APPROVED, ready to implement

---

## The Insight (Why We Changed)

### Original Approach ❌
- "Deploy ERC20 with 8% APY staking"
- Users earn yield passively
- Growth = larger supply circulating
- Leads to: speculation, yield farming, unsustainability

### New Approach ✅
- TST is an access token, not a reward token
- Users acquire TST to solve friction
- Growth = supply locked (scarcity)
- Leads to: operators, serious users, organic appreciation

**One quote that changed everything:**
> "If someone wants TST before they've used the product, something is wrong."

---

## What Changed

### 1. Token Supply Model

| Aspect | Old | New |
|--------|-----|-----|
| Supply | 1M (inflatable via rewards) | 1M (fixed forever) |
| Yield | 8% APY staking | 0% (no yield) |
| Inflation | Active (rewards mint) | Zero (no minting) |
| Intent | Investment | Access |

### 2. How TST is Used

**Old (Broken):**
```
User: "I want to earn yield"
System: "Stake TST, get 8% APY"
Result: User holds TST, doesn't use product
Outcome: Speculation, not usage
```

**New (Correct):**
```
User: "I want to create a P2P agreement"
System: "That requires 10 TST locked"
User: "Okay, I need TST to do this"
Result: User acquires TST for functional need
Outcome: Operator behavior, not speculation
```

### 3. Friction Points (What Drives TST Demand)

1. **P2P Agreement Creation**
   - Lock 10 TST for agreement duration
   - No yield, just collateral/commitment

2. **Priority Execution**
   - Stake 5 TST for faster strategy execution
   - Reduces cooldowns, no rewards

3. **Entity Compute Access**
   - Stake 5-100 TST for advanced analytics
   - No yield, just quota access

---

## Impact on Roadmap

### Phase 1 Week 2 (Now) ✅

**Old Plan:**
- Deploy ERC20 with staking contract
- Set up reward distribution
- Build "claim rewards" endpoint
- Position as income opportunity

**New Plan:**
- Deploy fixed-supply ERC20
- Deploy P2P escrow (locking)
- Deploy access tier staking (30-day periods)
- Deploy entity compute quota system
- Zero public announcement

### What This Prevents

❌ Yield farming (no yield to farm)
❌ Speculation (no promise of returns)
❌ Retail influx (no "buy cheap early" narrative)
❌ Regulatory issues (clear utility, not investment)
❌ Unsustainable mechanics (supply never grows)

---

## New Documents Created

### 1. **TST_NARRATIVE_FROZEN.md**
The constitution for TST.
- What TST CAN do ✅
- What TST will NEVER do ❌
- Red lines (if you see these, STOP)
- Enforcement mechanisms

**Key sections:**
- No promises about yield
- No investment positioning
- No inflation ever
- No marketing before Phase 2+

### 2. **TST_FRICTION_MECHANICS.md**
How the three friction points work.
- P2P agreement locking ($10, $50, $250+ tiers)
- Priority execution staking (5, 25, 100 TST)
- Entity compute access (usage-based quotas)
- UI patterns (what users see)

**Key sections:**
- Tier system (tied to real value, not just cosmetic)
- Lock vs stake (lock = permanent until expiry, stake = 30-day temp)
- Economics (scarcity through locking, not burning)
- Metrics to track (not price; usage, locks, tiers)

### 3. **SMART_CONTRACTS_TST_ACCESS_MODEL.md**
Smart contract specs without yield.
- TST.sol (fixed supply, no minting)
- P2PAgreementEscrow.sol (simple lock/unlock)
- AccessTierStaking.sol (30-day periods, no yield)
- EntityComputeReserve.sol (quota allocation)

**Key sections:**
- No staking rewards anywhere
- Fixed supply guarantee in code
- Simple access control (no complex logic)
- Security properties (immutable, no upgrades)

### 4. **PHASE1_WEEK2_ROADMAP_REVISED.md**
Day-by-day implementation plan.
- Days 1-2: Smart contracts (4 contracts, testnet)
- Day 3: Testnet deployment
- Days 4-5: API integration (5 new endpoints)
- Day 6: UI integration (show requirements, no prices)
- Day 7: Beta testing

**Key sections:**
- API endpoint specs (lock, stake, query, consume quota)
- Prisma models (TST_Lock, TST_Stake, EntityAccessTier)
- Success criteria (technical + product)
- Rollout plan (internal → beta → soft public)

---

## Key Differences

### TST Requirements (Access Tiers)

**Tier 0:** No TST (basic features)
```
- Create simple strategies
- 1 Risk analysis per day
- 24-hour execution cooldown
- $0 capital limit
```

**Tier 1:** 5 TST staked for 30 days
```
- Create P2P agreements up to $50K
- 3 Risk analyses per day
- 12-hour execution cooldown
- $50K capital limit
```

**Tier 2:** 25 TST staked for 30 days
```
- Create P2P agreements up to $500K
- 10 Risk analyses per day
- 1-hour execution cooldown
- $500K capital limit
```

**Tier 3:** 100+ TST staked for 30 days
```
- Unlimited P2P agreements
- Unlimited entity access
- Instant execution
- Unlimited capital limit
```

### No Yield Anywhere

**What we removed:**
```solidity
// ❌ These are GONE:
function stake(uint256 amount) external returns (uint256 rewards)
function claimStakingRewards() external returns (uint256 rewards)
function calculateAPY(uint256 amount) external view returns (uint256)
```

**What we kept:**
```solidity
// ✅ Only these:
function lockForAgreement(string id, uint256 amount, uint256 days) external
function stakeForTier(AccessTier tier) external
function unstake(uint256 stake_id) external  // Returns full TST, no penalties
```

---

## User Psychology Shift

### Old Model (Breaks)
1. User hears "8% APY"
2. User wants passive income
3. User buys TST speculatively
4. APY becomes unsustainable
5. Yields cut (user feels betrayed)
6. Exit cascade begins

### New Model (Works)
1. User wants to create P2P agreement
2. User learns: "Requires 10 TST locked"
3. User acquires TST for functional need
4. User has skin in the game (locked capital)
5. User committed (can't unstake immediately)
6. Repeat behavior becomes habitual

---

## Success Metrics Shift

### Old (Wrong)
```
- Price per TST
- Market cap
- Trading volume
- Holder count
- "Early adopters"
```

### New (Right)
```
- TST locked in agreements (growing?)
- Tier 1+ adoption (growing?)
- Average lock duration
- Re-stake rate (loyalty)
- Usage-to-holders ratio (serious users?)
```

**Benchmark (60 days):**
- 50-200 TST holders (not thousands)
- 70%+ of supply locked (not circulating)
- <5% traded (not actively pumped)
- Usage increasing week-over-week
- No marketing spend (organic only)

---

## Regulatory Advantage

### Old (Risky)
```
"Stake TST to earn 8% yield"
= Securities law red flag
= Investment contract classification
= May require SEC filing
```

### New (Clean)
```
"Acquire TST to unlock features"
= Clear utility classification
= Not an investment opportunity
= Regular token, properly categorized
```

---

## Timeline Implications

### When TST Becomes Public

**Not yet:** (Phase 1, Weeks 1-6)
- Zero external announcement
- Beta testers only
- Internal testing phase

**Week 7-12:** (Phase 2)
- Technical documentation published
- Architecture explained (not marketed)
- Selective developer audience

**Month 4+:** (Phase 3)
- Public documentation
- Selective exposure (builders, not retail)
- Institutional conversations

**Never:** (Red lines)
- "Early opportunity" messaging
- "Buy cheap before launch" posts
- Price predictions
- Yield promises

---

## Decision Freeze

**This approach is locked in.**

To change it, we need:
1. Explicit written approval from founder
2. Documentation of why
3. Verification it doesn't violate frozen narrative

**Current Status:** ✅ APPROVED for implementation

---

## What Success Looks Like

### 30 Days In
- 30-50 internal users with TST
- >100 TST locked in P2P agreements
- >50 TST staked for tiers
- 0% traded on secondary markets
- 0 external mentions

### 60 Days In
- 100-150 beta users with TST
- >500 TST locked
- >200 TST staked
- Still 0% speculation
- Only technical discussions

### 90 Days In
- 200+ active operators
- >2000 TST locked
- >1000 TST staked
- Supply down to ~7K circulating (93% locked)
- Natural appreciation without hype

---

## What Failure Looks Like

🛑 **Stop immediately if:**
- Someone asks "What's the price?"
- Marketing suggests "early opportunity"
- Yield farming yields are mentioned
- Comparison to other tokens emerges
- Anyone wants to "promote" TST

---

## Next Actions

**Before Phase 1 Week 2 starts:**

1. ✅ Founder approval (you just gave it)
2. ✅ Team awareness (share these 4 docs)
3. ✅ Engineer commitment (no yield = no shortcuts)
4. ✅ UI/UX review (no price displays anywhere)
5. ✅ Legal review (utility token classification)

**Day 1 of Week 2:**
- Start smart contract development
- Use SMART_CONTRACTS_TST_ACCESS_MODEL.md as spec
- No external announcement
- Internal Slack only

---

## References

- **TST_NARRATIVE_FROZEN.md** - What TST is (the constitution)
- **TST_FRICTION_MECHANICS.md** - How TST is used (the mechanics)
- **SMART_CONTRACTS_TST_ACCESS_MODEL.md** - Smart contract specs (the code)
- **PHASE1_WEEK2_ROADMAP_REVISED.md** - Implementation plan (the schedule)

---

## Summary

**We changed because:** Growth comes from friction, not marketing.

**We'll build:** Access token (not reward token)

**We'll measure:** Usage metrics (not price metrics)

**We'll defend:** Frozen narrative (not narrative drift)

**Result:** Institutional-grade token that actually drives behavior.

---

**Status: READY FOR PHASE 1 WEEK 2** ✅

Next: Approve this summary, then start smart contract development.
