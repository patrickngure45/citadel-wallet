# TST API Integration - Week 2 Days 4-5 Implementation

**Status:** Week 2, Day 3 → Ready for Backend Integration

---

## Overview

This document specifies the 5 FastAPI endpoints needed to integrate TST smart contracts with the existing wallet application.

**Timeline:** Days 4-5 (2 days)
**Effort:** ~16 hours
**Complexity:** Medium (mostly data mapping)

---

## Prisma Schema Updates

### Add to `schema.prisma`

```prisma
// TST Locking Records (P2P Agreements)
model TST_Lock {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation("user_tst_locks", fields: [userId], references: [id], onDelete: Cascade)
  
  // P2P Agreement Reference
  agreementId     String
  p2pAgreement    P2PAgreement? @relation(fields: [agreementId], references: [id], onDelete: Cascade)
  
  // Lock Details
  amount          BigInt   // Wei (e.g., 10 TST = 10*10^18)
  lockedUntil     DateTime
  released        Boolean  @default(false)
  releasedAt      DateTime?
  
  // Contract Reference
  contractLockId  String   // bytes32 from contract
  txHash          String?
  
  timestamps
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@index([userId])
  @@index([agreementId])
  @@index([released])
  @@unique([contractLockId])
}

// TST Staking Records (Access Tier)
model TST_Stake {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation("user_tst_stakes", fields: [userId], references: [id], onDelete: Cascade)
  
  // Tier Details
  tier            Int      // 1, 2, or 3
  amount          BigInt   // Wei (5, 25, or 100 TST)
  
  // Timing
  stakedAt        DateTime
  expiresAt       DateTime
  active          Boolean  @default(true)
  unstakedAt      DateTime?
  
  // Contract Reference
  contractStakeId String   // bytes32 from contract
  txHash          String?
  
  timestamps
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@index([userId])
  @@index([active])
  @@index([tier])
  @@unique([contractStakeId])
}

// Entity Access Tier Quotas
model EntityAccessTier {
  id              String   @id @default(cuid())
  userId          String
  user            User     @relation("user_entity_access", fields: [userId], references: [id], onDelete: Cascade)
  
  // Entity Type (1=Risk, 2=Strategy, 3=Memory)
  entityType      Int
  
  // Quota Details
  tstReserved     BigInt   // Wei
  quotaPerDay     Int      // From tier
  quotaUsedToday  Int      @default(0)
  lastResetTime   DateTime @default(now())
  
  // Contract Reference
  contractResId   String?  // bytes32 from contract
  
  timestamps
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@unique([userId, entityType])
  @@index([userId])
  @@index([entityType])
}

// Update existing models
model P2PAgreement {
  // ... existing fields ...
  
  // TST Integration
  tstLocks        TST_Lock[]
  tstLocked       Boolean  @default(false)  // Is TST locked?
  tstLockId       String?  // Reference to TST_Lock
  minTierRequired Int      @default(0)      // 0=none, 1, 2, or 3
}

model Strategy {
  // ... existing fields ...
  
  // TST Integration
  tstStakes       TST_Stake[]
  currentTier     Int      @default(0)      // 0, 1, 2, or 3
  tierExpiresAt   DateTime?
}

model User {
  // ... existing fields ...
  
  // TST Integration
  tstLocks        TST_Lock[] @relation("user_tst_locks")
  tstStakes       TST_Stake[] @relation("user_tst_stakes")
  entityAccess    EntityAccessTier[] @relation("user_entity_access")
  
  // Wallet Integration
  walletAddress   String?  @unique // EVM address for TST operations
}
```

---

## Migration Commands

```bash
# Generate migration
npx prisma migrate dev --name add_tst_integration

# Or reset database (dev only)
npx prisma migrate reset
```

---

## Endpoint 1: Lock TST for P2P Agreement

**Endpoint:** `POST /api/v1/p2p/{agreement_id}/lock-tst`

**Purpose:** Lock TST to create/enable P2P agreement

**Request:**
```python
{
  "amount": 10,           # TST amount
  "duration": 7776000     # seconds (90 days = 7776000)
}
```

**Response (201):**
```python
{
  "success": true,
  "lock": {
    "id": "lock_xyz",
    "lock_id": "0x...",  # bytes32 from contract
    "agreement_id": "agr_123",
    "amount": "10000000000000000000",  # 10 TST in Wei
    "locked_until": "2026-04-30T12:00:00Z",
    "status": "locked",
    "tx_hash": "0x..."
  },
  "tiers": {
    "tier_1": { "min_tst": 10, "max_amount": 50000 },
    "tier_2": { "min_tst": 50, "max_amount": 500000 },
    "tier_3": { "min_tst": 250, "max_amount": "unlimited" }
  }
}
```

**Error Responses:**

```python
# 400 - Invalid amount
{ "error": "Amount must match tier requirement (10, 50, or 250+ TST)" }

# 400 - Insufficient balance
{ "error": "Insufficient TST balance. Need 10 TST, have 5 TST" }

# 400 - Invalid duration
{ "error": "Duration must be between 1 and 365 days" }

# 404 - Agreement not found
{ "error": "Agreement not found" }

# 409 - Already locked
{ "error": "Agreement already has active TST lock" }
```

**Implementation:**
```python
from fastapi import APIRouter, HTTPException
from web3 import Web3
import asyncio

router = APIRouter(prefix="/api/v1")

@router.post("/p2p/{agreement_id}/lock-tst")
async def lock_tst_for_p2p(
    agreement_id: str,
    request: LockTSTRequest,
    user: User = Depends(get_current_user)
):
    # 1. Validate agreement exists and belongs to user
    agreement = db.session.query(P2PAgreement).filter(
        P2PAgreement.id == agreement_id,
        P2PAgreement.userId == user.id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # 2. Determine tier from amount
    tier_map = {10: 1, 50: 2, 250: 3}
    tier = tier_map.get(request.amount)
    if not tier:
        raise HTTPException(
            status_code=400,
            detail="Amount must match tier requirement (10, 50, or 250+ TST)"
        )
    
    # 3. Check user has TST balance
    user_balance = await get_tst_balance(user.wallet_address)
    if user_balance < request.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient TST balance. Need {request.amount} TST, have {user_balance} TST"
        )
    
    # 4. Validate duration
    if request.duration < 86400 or request.duration > 31536000:  # 1 day to 1 year
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 1 and 365 days"
        )
    
    # 5. Call contract lockForAgreement
    amount_wei = Web3.to_wei(request.amount, 'ether')
    tx_hash = await call_contract(
        "P2PAgreementEscrow",
        "lockForAgreement",
        amount_wei,
        request.duration,
        agreement_id
    )
    
    # 6. Wait for confirmation
    receipt = await wait_for_transaction(tx_hash)
    lock_id = extract_lock_id_from_receipt(receipt)
    
    # 7. Store in database
    lock = TST_Lock(
        userId=user.id,
        agreementId=agreement_id,
        amount=amount_wei,
        lockedUntil=datetime.now() + timedelta(seconds=request.duration),
        contractLockId=lock_id,
        txHash=tx_hash
    )
    db.session.add(lock)
    
    # 8. Update agreement
    agreement.tstLocked = True
    agreement.tstLockId = lock.id
    agreement.minTierRequired = tier
    db.session.commit()
    
    return {
        "success": True,
        "lock": {
            "id": lock.id,
            "lock_id": lock_id,
            "agreement_id": agreement_id,
            "amount": str(amount_wei),
            "locked_until": lock.lockedUntil.isoformat() + "Z",
            "status": "locked",
            "tx_hash": tx_hash
        }
    }
```

---

## Endpoint 2: Upgrade Tier (Stake TST)

**Endpoint:** `POST /api/v1/strategies/{strategy_id}/upgrade-tier`

**Purpose:** Stake TST for access tier (30-day lock)

**Request:**
```python
{
  "tier": 2  # 1, 2, or 3
}
```

**Response (201):**
```python
{
  "success": true,
  "stake": {
    "id": "stake_abc",
    "stake_id": "0x...",  # bytes32 from contract
    "tier": 2,
    "amount": "25000000000000000000",  # 25 TST in Wei
    "staked_at": "2026-01-30T12:00:00Z",
    "expires_at": "2026-02-29T12:00:00Z",
    "benefits": {
      "entity_analysis_per_day": 10,
      "execution_wait_time": "1 hour",
      "priority_level": "high"
    },
    "tx_hash": "0x..."
  }
}
```

**Error Responses:**

```python
# 400 - Invalid tier
{ "error": "Tier must be 1, 2, or 3" }

# 400 - Insufficient balance
{ "error": "Insufficient TST balance for Tier 2 (need 25 TST, have 10 TST)" }

# 409 - Already has tier
{ "error": "Strategy already has active Tier 3 stake (expires 2026-02-29)" }

# 404 - Strategy not found
{ "error": "Strategy not found" }
```

**Implementation:**
```python
@router.post("/strategies/{strategy_id}/upgrade-tier")
async def upgrade_tier(
    strategy_id: str,
    request: UpgradeTierRequest,
    user: User = Depends(get_current_user)
):
    # 1. Validate strategy exists
    strategy = db.session.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.userId == user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # 2. Validate tier
    if request.tier not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Tier must be 1, 2, or 3")
    
    # 3. Get tier amount
    tier_amounts = {
        1: 5,
        2: 25,
        3: 100
    }
    required_amount = tier_amounts[request.tier]
    
    # 4. Check if user already has tier
    active_stake = db.session.query(TST_Stake).filter(
        TST_Stake.userId == user.id,
        TST_Stake.active == True,
        TST_Stake.expiresAt > datetime.now()
    ).first()
    
    if active_stake:
        raise HTTPException(
            status_code=409,
            detail=f"Already has active Tier {active_stake.tier} stake (expires {active_stake.expiresAt.isoformat()})"
        )
    
    # 5. Check balance
    balance = await get_tst_balance(user.wallet_address)
    if balance < required_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient TST balance for Tier {request.tier} (need {required_amount} TST, have {balance} TST)"
        )
    
    # 6. Call contract stakeForTier
    amount_wei = Web3.to_wei(required_amount, 'ether')
    tx_hash = await call_contract(
        "AccessTierStaking",
        "stakeForTier",
        request.tier
    )
    
    # 7. Wait for confirmation
    receipt = await wait_for_transaction(tx_hash)
    stake_id = extract_stake_id_from_receipt(receipt)
    
    # 8. Store in database
    expires_at = datetime.now() + timedelta(days=30)
    stake = TST_Stake(
        userId=user.id,
        tier=request.tier,
        amount=amount_wei,
        stakedAt=datetime.now(),
        expiresAt=expires_at,
        contractStakeId=stake_id,
        txHash=tx_hash
    )
    db.session.add(stake)
    
    # 9. Update strategy
    strategy.currentTier = request.tier
    strategy.tierExpiresAt = expires_at
    db.session.commit()
    
    # 10. Return response
    tier_benefits = {
        1: {"analyses": 3, "wait": "12 hours"},
        2: {"analyses": 10, "wait": "1 hour"},
        3: {"analyses": "unlimited", "wait": "instant"}
    }
    
    return {
        "success": True,
        "stake": {
            "id": stake.id,
            "stake_id": stake_id,
            "tier": request.tier,
            "amount": str(amount_wei),
            "staked_at": stake.stakedAt.isoformat() + "Z",
            "expires_at": expires_at.isoformat() + "Z",
            "benefits": {
                "entity_analysis_per_day": tier_benefits[request.tier]["analyses"],
                "execution_wait_time": tier_benefits[request.tier]["wait"],
                "priority_level": ["low", "medium", "high"][request.tier - 1]
            },
            "tx_hash": tx_hash
        }
    }
```

---

## Endpoint 3: Reserve Entity Compute Access

**Endpoint:** `POST /api/v1/entities/{entity_id}/reserve-compute`

**Purpose:** Reserve TST for entity compute access (if staked)

**Request:**
```python
{
  "entity_type": 1  # 1=Risk, 2=Strategy, 3=Memory
}
```

**Response (201):**
```python
{
  "success": true,
  "reservation": {
    "id": "res_xyz",
    "reservation_id": "0x...",  # bytes32 from contract
    "entity_type": 1,
    "entity_name": "Risk",
    "tier": 2,
    "quota_today": 10,
    "quota_remaining": 10,
    "last_reset": "2026-01-30T00:00:00Z",
    "next_reset": "2026-01-31T00:00:00Z",
    "expires_at": "2026-02-29T12:00:00Z"
  }
}
```

**Error Responses:**

```python
# 400 - Invalid entity
{ "error": "Entity type must be 1 (Risk), 2 (Strategy), or 3 (Memory)" }

# 409 - No active tier
{ "error": "No active TST tier. Stake TST to enable entity access" }

# 409 - Already reserved
{ "error": "Entity already has active reservation" }
```

**Implementation:**
```python
@router.post("/entities/{entity_id}/reserve-compute")
async def reserve_entity_compute(
    entity_id: str,
    request: ReserveComputeRequest,
    user: User = Depends(get_current_user)
):
    # 1. Validate entity type
    if request.entity_type not in [1, 2, 3]:
        raise HTTPException(
            status_code=400,
            detail="Entity type must be 1 (Risk), 2 (Strategy), or 3 (Memory)"
        )
    
    # 2. Check user has active tier
    active_stake = db.session.query(TST_Stake).filter(
        TST_Stake.userId == user.id,
        TST_Stake.active == True,
        TST_Stake.expiresAt > datetime.now()
    ).first()
    
    if not active_stake:
        raise HTTPException(
            status_code=409,
            detail="No active TST tier. Stake TST to enable entity access"
        )
    
    # 3. Check for existing reservation
    existing = db.session.query(EntityAccessTier).filter(
        EntityAccessTier.userId == user.id,
        EntityAccessTier.entityType == request.entity_type
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Entity already has active reservation"
        )
    
    # 4. Get quota for tier and entity
    tier = active_stake.tier
    quotas = {
        1: {1: 3, 2: 12, 3: 7},   # Tier 1
        2: {1: 10, 2: 28, 3: 28}, # Tier 2
        3: {1: 1000, 2: 1000, 3: 1000}  # Tier 3
    }
    quota_per_day = quotas[tier][request.entity_type]
    
    # 5. Store in database
    access = EntityAccessTier(
        userId=user.id,
        entityType=request.entity_type,
        tstReserved=active_stake.amount,
        quotaPerDay=quota_per_day,
        quotaUsedToday=0,
        lastResetTime=datetime.now()
    )
    db.session.add(access)
    db.session.commit()
    
    entity_names = {1: "Risk", 2: "Strategy", 3: "Memory"}
    
    return {
        "success": True,
        "reservation": {
            "id": access.id,
            "reservation_id": access.contractResId or "pending",
            "entity_type": request.entity_type,
            "entity_name": entity_names[request.entity_type],
            "tier": tier,
            "quota_today": quota_per_day,
            "quota_remaining": quota_per_day,
            "last_reset": access.lastResetTime.isoformat() + "Z",
            "next_reset": (access.lastResetTime + timedelta(days=1)).isoformat() + "Z",
            "expires_at": active_stake.expiresAt.isoformat() + "Z"
        }
    }
```

---

## Endpoint 4: Check TST Requirements

**Endpoint:** `GET /api/v1/tst/requirements/{action}`

**Purpose:** Display TST requirements for actions

**Query Parameters:**
- `action`: `lock_p2p`, `upgrade_tier`, `reserve_entity`

**Response:**
```python
{
  "action": "lock_p2p",
  "description": "Lock TST for P2P agreement",
  "tiers": [
    {
      "tier": 1,
      "tst_required": 10,
      "max_agreement_value": 50000,
      "requirement": "Lock for agreement duration"
    },
    {
      "tier": 2,
      "tst_required": 50,
      "max_agreement_value": 500000,
      "requirement": "Lock for agreement duration"
    },
    {
      "tier": 3,
      "tst_required": 250,
      "max_agreement_value": "unlimited",
      "requirement": "Lock for agreement duration"
    }
  ]
}
```

**Implementation:**
```python
@router.get("/tst/requirements/{action}")
async def get_tst_requirements(action: str):
    requirements = {
        "lock_p2p": {
            "description": "Lock TST for P2P agreement",
            "tiers": [
                {"tier": 1, "tst": 10, "max": 50000},
                {"tier": 2, "tst": 50, "max": 500000},
                {"tier": 3, "tst": 250, "max": "unlimited"}
            ]
        },
        "upgrade_tier": {
            "description": "Stake TST for access tier",
            "tiers": [
                {"tier": 1, "tst": 5, "duration": "30 days"},
                {"tier": 2, "tst": 25, "duration": "30 days"},
                {"tier": 3, "tst": 100, "duration": "30 days"}
            ]
        },
        "reserve_entity": {
            "description": "Reserve TST for entity access",
            "tiers": [
                {"tier": 1, "tst": 5, "per_day": "variable"},
                {"tier": 2, "tst": 25, "per_day": "variable"},
                {"tier": 3, "tst": 100, "per_day": "unlimited"}
            ]
        }
    }
    
    if action not in requirements:
        raise HTTPException(status_code=404, detail="Unknown action")
    
    return requirements[action]
```

---

## Endpoint 5: Check User TST Access

**Endpoint:** `GET /api/v1/tst/access/{user_id}`

**Purpose:** Show user's current TST access and quotas

**Response:**
```python
{
  "user_id": "user_123",
  "current_tier": 2,
  "tier_active_until": "2026-02-29T12:00:00Z",
  "tst_balance": "500000000000000000",  # 0.5 TST in Wei
  "tst_staked": "25000000000000000000",  # 25 TST in Wei
  "tst_locked": "50000000000000000000",  # 50 TST in Wei
  "tst_available": "425000000000000000000",  # Available for new locks
  "locks": [
    {
      "lock_id": "lock_xyz",
      "agreement_id": "agr_123",
      "amount": "50000000000000000000",
      "locked_until": "2026-04-30T12:00:00Z",
      "status": "active",
      "days_remaining": 90
    }
  ],
  "entity_quotas": {
    "risk": {
      "available": 8,
      "total": 10,
      "reset_at": "2026-01-31T00:00:00Z"
    },
    "strategy": {
      "available": 28,
      "total": 28,
      "reset_at": "2026-01-31T00:00:00Z"
    },
    "memory": {
      "available": 28,
      "total": 28,
      "reset_at": "2026-01-31T00:00:00Z"
    }
  }
}
```

**Implementation:**
```python
@router.get("/tst/access/{user_id}")
async def get_tst_access(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    # Only users can see their own access
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get active tier
    active_stake = db.session.query(TST_Stake).filter(
        TST_Stake.userId == user_id,
        TST_Stake.active == True,
        TST_Stake.expiresAt > datetime.now()
    ).first()
    
    current_tier = active_stake.tier if active_stake else 0
    
    # Get balances
    balance = await get_tst_balance(user.wallet_address)
    
    staked = db.session.query(func.sum(TST_Stake.amount)).filter(
        TST_Stake.userId == user_id,
        TST_Stake.active == True
    ).scalar() or 0
    
    locked = db.session.query(func.sum(TST_Lock.amount)).filter(
        TST_Lock.userId == user_id,
        TST_Lock.released == False
    ).scalar() or 0
    
    # Get locks
    locks = db.session.query(TST_Lock).filter(
        TST_Lock.userId == user_id,
        TST_Lock.released == False
    ).all()
    
    lock_list = [
        {
            "lock_id": lock.contractLockId,
            "agreement_id": lock.agreementId,
            "amount": str(lock.amount),
            "locked_until": lock.lockedUntil.isoformat() + "Z",
            "status": "active",
            "days_remaining": (lock.lockedUntil - datetime.now()).days
        }
        for lock in locks
    ]
    
    # Get entity quotas
    entity_access = db.session.query(EntityAccessTier).filter(
        EntityAccessTier.userId == user_id
    ).all()
    
    entity_names = {1: "risk", 2: "strategy", 3: "memory"}
    quotas = {}
    
    for entity in entity_access:
        # Check if quota needs reset
        hours_since_reset = (datetime.now() - entity.lastResetTime).total_seconds() / 3600
        if hours_since_reset >= 24:
            entity.quotaUsedToday = 0
            entity.lastResetTime = datetime.now()
            db.session.commit()
        
        quotas[entity_names[entity.entityType]] = {
            "available": entity.quotaPerDay - entity.quotaUsedToday,
            "total": entity.quotaPerDay,
            "reset_at": (entity.lastResetTime + timedelta(days=1)).isoformat() + "Z"
        }
    
    return {
        "user_id": user_id,
        "current_tier": current_tier,
        "tier_active_until": active_stake.expiresAt.isoformat() + "Z" if active_stake else None,
        "tst_balance": str(balance),
        "tst_staked": str(staked),
        "tst_locked": str(locked),
        "tst_available": str(balance - staked - locked),
        "locks": lock_list,
        "entity_quotas": quotas
    }
```

---

## Testing Scenarios

### Test 1: Lock P2P Agreement
1. Create P2P agreement as User A
2. Call `/p2p/{id}/lock-tst` with amount=10
3. Verify TST locked in contract
4. Verify 90-day countdown starts
5. After 90 days, release and verify TST returned

### Test 2: Upgrade Tier
1. Call `/strategies/{id}/upgrade-tier` with tier=2
2. Verify TST staked (25 TST)
3. Verify tier active for 30 days
4. Wait 30 days, call unstake
5. Verify TST returned

### Test 3: Reserve Entity Access
1. Stake TST for tier (tier=2)
2. Call `/entities/{id}/reserve-compute` with entity_type=1
3. Verify quota initialized (10 per day for tier 2)
4. Call API to consume 1 quota
5. Verify remaining = 9
6. Wait 24h, verify reset to 10

### Test 4: Check Requirements
1. Call `/tst/requirements/lock_p2p`
2. Verify 3 tiers returned with correct amounts

### Test 5: Check Access
1. User with Tier 2 + 1 lock + 2 entity quotas
2. Call `/tst/access/{user_id}`
3. Verify all data returned correctly

---

**Status:** Ready for Days 4-5 Backend Implementation ✅
