# Smart Contracts Specification (REVISED)

## TST Access Model

**Updated:** January 30, 2026  
**Paradigm Shift:** From staking rewards → access token + locking  
**Status:** Phase 1 Week 2 (Implementation ready)

---

## Core Principle

TST is **not** a reward token. TST is an **access token** that gates functionality through locking and staking.

Users acquire TST to solve friction points:
- Create P2P agreements (lock)
- Execute strategies faster (stake)
- Access advanced entities (stake)

**No yield. No inflation. No promises.**

---

## 1. TST TOKEN CONTRACT

**File:** `contracts/TST.sol`  
**Type:** ERC-20 + Access Control + Locking  
**Networks:** BSC (primary), Polygon (secondary)

### Specification

```solidity
// Core ERC-20
contract TST is ERC20, Ownable {
    // Fixed supply (no minting, no inflation)
    uint256 constant TOTAL_SUPPLY = 1_000_000e18;
    
    // Constructor
    constructor() ERC20("TradeSynapse Token", "TST") {
        _mint(owner(), TOTAL_SUPPLY);
    }
    
    // Access control tiers (no yield)
    mapping(address => LockRecord[]) public locks;
    mapping(address => StakeRecord[]) public stakes;
    
    // Events
    event TokenLocked(address indexed user, uint256 amount, uint256 until, string reason);
    event TokenStaked(address indexed user, uint256 amount, uint256 duration, string tier);
    event TokenUnlocked(address indexed user, uint256 amount);
    event TokenUnstaked(address indexed user, uint256 amount);
}
```

### Key Features

✅ **Fixed Supply**
- 1M TST total (no inflation ever)
- No minting, no rewards, no dilution

✅ **No Yield Mechanism**
- TST doesn't earn rewards
- Value comes from access, not passive income

✅ **Locking Mechanism**
- Lock TST for P2P agreements
- Lock duration = agreement duration
- User recovers TST when lock expires

✅ **Staking Mechanism**
- Temporary stakes for access tiers
- 5 TST = Tier 1 (30 days)
- 25 TST = Tier 2 (30 days)
- 100 TST = Tier 3 (30 days)
- No yield, just access

✅ **Access Control**
- Tier 0: No TST (basic features)
- Tier 1: 5 TST staked (priority execution)
- Tier 2: 25 TST staked (advanced entities)
- Tier 3: 100+ TST staked (all features)

---

## 2. P2P AGREEMENT ESCROW CONTRACT

**File:** `contracts/P2PAgreementEscrow.sol`  
**Purpose:** Lock TST for P2P agreement duration  
**Pattern:** Simple escrow, no complex logic

### Specification

```solidity
contract P2PAgreementEscrow {
    struct AgreementLock {
        address creator;
        uint256 tst_amount;
        uint256 locked_until;
        string agreement_id;
        bool released;
    }
    
    mapping(string => AgreementLock) public locks;
    TST public tst_token;
    
    // Lock TST for agreement
    function lockForAgreement(
        string memory agreement_id,
        uint256 tst_amount,
        uint256 duration_seconds
    ) external {
        require(tst_amount >= 10e18, "Minimum: 10 TST");
        
        // Transfer TST from user to escrow
        tst_token.transferFrom(msg.sender, address(this), tst_amount);
        
        // Record lock
        locks[agreement_id] = AgreementLock({
            creator: msg.sender,
            tst_amount: tst_amount,
            locked_until: block.timestamp + duration_seconds,
            agreement_id: agreement_id,
            released: false
        });
        
        emit TokenLocked(msg.sender, tst_amount, locks[agreement_id].locked_until, "p2p_agreement");
    }
    
    // Release TST when agreement expires
    function releaseAfterExpiry(string memory agreement_id) external {
        AgreementLock storage lock = locks[agreement_id];
        require(block.timestamp >= lock.locked_until, "Agreement still active");
        require(!lock.released, "Already released");
        
        lock.released = true;
        tst_token.transfer(lock.creator, lock.tst_amount);
        emit TokenUnlocked(lock.creator, lock.tst_amount);
    }
    
    // Emergency: Terminate agreement early
    function earlyTerminate(string memory agreement_id) external {
        AgreementLock storage lock = locks[agreement_id];
        require(lock.creator == msg.sender, "Only creator can terminate");
        require(!lock.released, "Already released");
        
        lock.released = true;
        tst_token.transfer(lock.creator, lock.tst_amount);
        emit TokenUnlocked(lock.creator, lock.tst_amount);
    }
    
    function isLocked(string memory agreement_id) external view returns (bool) {
        AgreementLock memory lock = locks[agreement_id];
        return !lock.released && block.timestamp < lock.locked_until;
    }
}
```

**Key Points:**
- ✅ TST is locked, then released (never burned)
- ✅ Lock duration tied to agreement
- ✅ Early termination allowed (no penalties)
- ✅ No yield, no rewards, pure escrow

---

## 3. ACCESS TIER STAKING CONTRACT

**File:** `contracts/AccessTierStaking.sol`  
**Purpose:** Temporary TST stakes for feature access  
**Duration:** 30-day tiers, auto-renew optional

### Specification

```solidity
contract AccessTierStaking {
    enum AccessTier { NONE, TIER_1, TIER_2, TIER_3 }
    
    struct StakeRecord {
        address user;
        uint256 tst_amount;
        AccessTier tier;
        uint256 stake_date;
        uint256 expires_at;
        bool active;
    }
    
    mapping(address => StakeRecord[]) public stakes;
    mapping(address => AccessTier) public currentTier;
    TST public tst_token;
    
    // Tier requirements
    uint256 constant TIER_1_AMOUNT = 5e18;      // 5 TST
    uint256 constant TIER_2_AMOUNT = 25e18;     // 25 TST
    uint256 constant TIER_3_AMOUNT = 100e18;    // 100 TST
    uint256 constant STAKE_DURATION = 30 days;
    
    // Stake for access tier (30-day period)
    function stakeForTier(AccessTier tier) external {
        uint256 amount = _tierToAmount(tier);
        require(amount > 0, "Invalid tier");
        
        // Transfer TST from user
        tst_token.transferFrom(msg.sender, address(this), amount);
        
        // Create stake record
        StakeRecord memory record = StakeRecord({
            user: msg.sender,
            tst_amount: amount,
            tier: tier,
            stake_date: block.timestamp,
            expires_at: block.timestamp + STAKE_DURATION,
            active: true
        });
        
        stakes[msg.sender].push(record);
        currentTier[msg.sender] = tier;
        
        emit TokenStaked(msg.sender, amount, STAKE_DURATION, _tierName(tier));
    }
    
    // Check if user has active tier
    function hasActiveTier(address user, AccessTier minimum_tier) external view returns (bool) {
        AccessTier current = currentTier[user];
        if (current < minimum_tier) return false;
        
        // Find latest stake
        for (uint i = stakes[user].length; i > 0; i--) {
            StakeRecord memory record = stakes[user][i - 1];
            if (record.active && block.timestamp < record.expires_at) {
                return true;
            }
        }
        
        return false;
    }
    
    // Unstake after 30 days (TST returned, no penalties)
    function unstake(uint256 stake_index) external {
        StakeRecord storage record = stakes[msg.sender][stake_index];
        require(record.active, "Already unstaked");
        require(block.timestamp >= record.expires_at, "Still staking");
        
        record.active = false;
        currentTier[msg.sender] = AccessTier.NONE;
        
        // Return full amount (no penalties, no yield)
        tst_token.transfer(msg.sender, record.tst_amount);
        
        emit TokenUnstaked(msg.sender, record.tst_amount);
    }
    
    function _tierToAmount(AccessTier tier) internal pure returns (uint256) {
        if (tier == AccessTier.TIER_1) return TIER_1_AMOUNT;
        if (tier == AccessTier.TIER_2) return TIER_2_AMOUNT;
        if (tier == AccessTier.TIER_3) return TIER_3_AMOUNT;
        return 0;
    }
    
    function _tierName(AccessTier tier) internal pure returns (string memory) {
        if (tier == AccessTier.TIER_1) return "priority_execution";
        if (tier == AccessTier.TIER_2) return "advanced_entities";
        if (tier == AccessTier.TIER_3) return "institution_access";
        return "none";
    }
}
```

**Key Points:**
- ✅ 30-day stakes only (no perpetual locking)
- ✅ No yield, no penalties, full principal returned
- ✅ Auto-unstakable after 30 days
- ✅ Tier upgrades in API layer (contract just manages access)

---

## 4. ENTITY COMPUTE RESERVATION CONTRACT

**File:** `contracts/EntityComputeReserve.sol`  
**Purpose:** Reserve TST for advanced entity access  
**Allocation:** Usage-based quota system

### Specification

```solidity
contract EntityComputeReserve {
    enum EntityType { RISK, STRATEGY, MEMORY, PERCEPTION }
    
    struct ComputeAllocation {
        address user;
        EntityType entity;
        uint256 tst_reserved;
        uint256 quota_per_day;
        uint256 quota_used_today;
        uint256 last_reset;
        bool active;
    }
    
    mapping(address => mapping(EntityType => ComputeAllocation)) public allocations;
    TST public tst_token;
    
    // Reserve TST for entity access (30-day period)
    function reserveForEntity(
        EntityType entity,
        uint256 days_duration
    ) external {
        uint256 tst_amount = _entityToAmount(entity);
        require(tst_amount > 0, "Invalid entity");
        require(days_duration <= 30, "Max 30 days");
        
        // Transfer TST
        tst_token.transferFrom(msg.sender, address(this), tst_amount);
        
        // Create allocation
        allocations[msg.sender][entity] = ComputeAllocation({
            user: msg.sender,
            entity: entity,
            tst_reserved: tst_amount,
            quota_per_day: _entityToQuota(entity),
            quota_used_today: 0,
            last_reset: block.timestamp,
            active: true
        });
        
        emit TokenStaked(msg.sender, tst_amount, days_duration * 1 days, _entityName(entity));
    }
    
    // Check available quota for entity
    function getQuotaRemaining(
        address user,
        EntityType entity
    ) external view returns (uint256) {
        ComputeAllocation memory alloc = allocations[user][entity];
        if (!alloc.active) return 0;
        
        // Reset quota if day changed
        if (block.timestamp > alloc.last_reset + 1 days) {
            return alloc.quota_per_day;
        }
        
        return alloc.quota_per_day - alloc.quota_used_today;
    }
    
    // Consume quota (called from API after verification)
    function consumeQuota(address user, EntityType entity) external {
        require(msg.sender == owner(), "Only backend can call");
        
        ComputeAllocation storage alloc = allocations[user][entity];
        require(alloc.active, "No active allocation");
        
        // Reset quota if needed
        if (block.timestamp > alloc.last_reset + 1 days) {
            alloc.quota_used_today = 0;
            alloc.last_reset = block.timestamp;
        }
        
        alloc.quota_used_today += 1;
        require(alloc.quota_used_today <= alloc.quota_per_day, "Quota exceeded");
    }
    
    function _entityToAmount(EntityType entity) internal pure returns (uint256) {
        if (entity == EntityType.RISK) return 5e18;
        if (entity == EntityType.STRATEGY) return 10e18;
        if (entity == EntityType.MEMORY) return 15e18;
        return 0;
    }
    
    function _entityToQuota(EntityType entity) internal pure returns (uint256) {
        if (entity == EntityType.RISK) return 10;
        if (entity == EntityType.STRATEGY) return 5;
        if (entity == EntityType.MEMORY) return 3;
        return 1;
    }
}
```

**Key Points:**
- ✅ Usage-based quota (more TST = more queries)
- ✅ Daily reset of quota
- ✅ No yield, just allocation
- ✅ Backend verifies quota consumption

---

## 5. GOVERNANCE TOKEN (Future)

**File:** `contracts/Governance.sol`  
**Status:** Phase 2 (not needed for Phase 1)  
**Purpose:** DAO voting on TST mechanics changes

Will implement when:
- 1000+ active users
- TST adoption stable
- Community ready for governance

---

## Deployment Checklist

**Before Mainnet:**

- [ ] Professional audit (TBD audit firm)
- [ ] Formal verification (if budget allows)
- [ ] Test coverage >95%
- [ ] Gas optimization complete
- [ ] Access controls locked
- [ ] No upgradeable proxies (immutable)

**Deployment Order:**

1. Deploy TST (fixed supply)
2. Deploy P2PAgreementEscrow
3. Deploy AccessTierStaking
4. Deploy EntityComputeReserve
5. Wire in FastAPI backend
6. Beta test with internal users (1 week)
7. Launch to beta users (public)

---

## Key Differences from Original Plan

❌ **Removed:**
- Staking rewards (APY)
- Liquidity mining
- Airdrop mechanism
- Minting capabilities
- Any inflation mechanics

✅ **Added:**
- Fixed supply (1M TST, never changes)
- Access control tiers
- Locking mechanism (P2P escrow)
- Temporary staking (30-day periods)
- Usage-based quotas
- No yield, no promises

---

## Security Properties

✅ **No External Dependencies**
- All logic self-contained in contracts
- No oracles, no external calls
- No upgradeable proxies

✅ **Simple Access Control**
- Only owner can call sensitive functions
- Backend verifies quotas
- No complex governance initially

✅ **Fixed Supply Guarantee**
- 1M TST locked at deployment
- No minting after genesis
- Can't create inflation

✅ **User Protection**
- No penalties for early unstaking
- TST always returned (locking ≠ burning)
- Clear tier requirements upfront

---

## What This Prevents

❌ **Regulatory Risk**
- TST is not an "investment" (no yield promises)
- No securities law violations
- Clear utility classification

❌ **Unsustainable Mechanics**
- Can't promise yield we can't sustain
- Supply fixed (no inflation trap)
- Access model is defensible

❌ **Speculative Attack**
- No price discovery until Phase 3+
- No liquidity to exploit
- No reward mechanisms to gamify

---

## Integration Points

**FastAPI Backend:**

```python
from contracts import TST, AccessTierStaking, EntityComputeReserve

# Check if user can create P2P agreement
can_create = escrow.isValidForAgreement(user_id, amount)

# Check if user has access tier
has_tier = staking.hasActiveTier(user_address, TIER_1)

# Check entity quota
quota_remaining = compute_reserve.getQuotaRemaining(user, ENTITY_RISK)

# Consume quota after entity runs
compute_reserve.consumeQuota(user, ENTITY_RISK)
```

**Prisma Database:**

```prisma
model TST_Lock {
  id String @id @default(cuid())
  user_id String
  amount Decimal
  reason String  // "p2p_agreement", "entity_compute"
  locked_until DateTime
  released Boolean @default(false)
  created_at DateTime @default(now())
}

model TST_Stake {
  id String @id @default(cuid())
  user_id String
  amount Decimal
  tier String  // "tier_1", "tier_2", "tier_3"
  expires_at DateTime
  active Boolean @default(true)
  created_at DateTime @default(now())
}
```

---

## Success Metrics

✅ **Track These:**
- Total TST locked (should grow)
- Active users on Tier 1+ (should grow)
- Average lock duration
- Entity compute reservations
- Weekly retention (users re-staking)

❌ **Don't Track These:**
- Price
- Volume
- Market cap
- Social sentiment
- Holder count (not important)

---

## Phase 1 Week 2 Timeline

| Day | Task |
|-----|------|
| 1-2 | Smart contract development |
| 3 | Internal testing |
| 4 | Deploy to testnet |
| 5 | Beta user testing |
| 6 | Backend integration |
| 7 | API endpoints for access control |

**No public announcement until Phase 2+**
