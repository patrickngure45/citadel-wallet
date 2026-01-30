# Citadel Deposit System

Complete user deposit detection, verification, and settlement flow with autonomous entity governance.

## Overview

The Deposit System handles:
1. **Detection**: Monitor blockchain for transfers to user wallets
2. **Verification**: Link deposits to users and validate ownership
3. **Entity Approval**: Risk + Strategy entities verify before settlement
4. **Settlement**: Sweep funds to MASTER_WALLET with 2-of-3 multi-sig
5. **Database**: Record transactions, credit balances, award TST tokens
6. **Audit Trail**: Compliance logging of entire workflow

## Architecture

### Three-Stage Settlement Flow

```
STAGE 1: DETECTION
┌─────────────────────────────────────────────────────────┐
│ User deposits $500 USDT to user wallet (on-chain)      │
│ Blockchain monitor detects transfer                     │
│ DepositListener creates Deposit object                  │
│ Status: DETECTED                                        │
└─────────────────────────────────────────────────────────┘
                          ↓
STAGE 2: ENTITY VERIFICATION
┌─────────────────────────────────────────────────────────┐
│ Risk Entity (3-min cycle):                              │
│   - Anomaly detection model                             │
│   - Check user history                                  │
│   - Score: 0.01 (normal) ✓                             │
│                                                          │
│ Strategy Entity (2-min cycle):                          │
│   - Portfolio alignment check                           │
│   - Allocation rules validation                         │
│   - Score: 0.92 (aligned) ✓                            │
│                                                          │
│ Status: VERIFIED → APPROVED                             │
│ TST Reward: 5 TST (1 per $100)                         │
└─────────────────────────────────────────────────────────┘
                          ↓
STAGE 3: SETTLEMENT & DATABASE
┌─────────────────────────────────────────────────────────┐
│ FundSettlement creates sweep transaction:               │
│   From: 0x578FC73... (user wallet)                     │
│   To: 0xf5C649... (MASTER_WALLET)                      │
│   Amount: $500 USDT                                     │
│   Status: SWEEPING                                      │
│                                                          │
│ Multi-Sig Signing (2-of-3):                            │
│   - Risk Entity signature (approved)                    │
│   - Strategy Entity signature (approved)                │
│   - Execution Entity broadcasts                         │
│                                                          │
│ Sweep TX confirmed on-chain                             │
│ Status: SWEPT → SETTLED                                │
│                                                          │
│ Database Updates:                                       │
│   - Transaction record created                          │
│   - User balance credited: +$500 USDT                  │
│   - TST tokens awarded: +5 TST                         │
│   - Performance metrics updated                         │
│   - Audit trail logged                                 │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. DepositListener (`backend/deposit/listener.py`)

Monitors blockchain for transfers to user wallets.

**Classes:**
- `Deposit`: Represents single deposit event
  - Properties: tx_hash, from/to addresses, amount, asset, chain
  - Status: DETECTED → VERIFIED → APPROVED → SWEEPING → SWEPT → SETTLED
  - Methods: mark_verified(), mark_approved(), mark_swept(), mark_settled()

- `DepositListener`: Blockchain monitoring
  - Web3 providers for BSC and Polygon
  - `process_transfer_event()`: Detect transfers
  - `calculate_tst_reward()`: 1 TST per $100
  - `mark_*()`: Status progression
  - Pending/settled deposit tracking

- `FundSettlement`: Sweep orchestration
  - `queue_for_settlement()`: Add to sweep queue
  - `create_sweep_transaction()`: Create multi-sig TX
  - `process_sweep_confirmation()`: Handle on-chain confirmation

**Example:**
```python
listener = DepositListener({
    "bsc": "https://bsc-dataseed1.binance.org",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"
})

# Detect deposit
deposit = listener.process_transfer_event(
    from_address="0xSender...",
    to_address="0x578FC73...",  # User wallet
    amount=Decimal("500"),
    asset_type="usdt",
    chain="bsc",
    tx_hash="0x1234567890abcdef",
    block_number=45123456,
    timestamp=datetime.utcnow()
)

# Calculate reward
tst_reward = listener.calculate_tst_reward(Decimal("500"))  # Returns 5
```

### 2. DepositDatabaseManager (`backend/deposit/database.py`)

Handles all database updates during settlement.

**Methods:**
- `record_deposit_transaction()`: Create transaction record
- `confirm_deposit_transaction()`: Mark confirmed on-chain
- `record_sweep_transaction()`: Track sweep TX
- `credit_user_balance()`: Update pocket balance
- `award_tst_tokens()`: Create TST stake record
- `update_performance_metrics()`: Daily tracking
- `log_settlement_audit()`: Compliance logging

**Example:**
```python
db_manager = DepositDatabaseManager(db)

# Record deposit
await db_manager.record_deposit_transaction(
    wallet_id="wallet_123",
    tx_hash="0x1234567890abcdef",
    deposit_amount=Decimal("500"),
    asset_type="usdt",
    chain="bsc",
    from_address="0xSender...",
    to_address="0x578FC73..."
)

# Award TST
success, stake = await db_manager.award_tst_tokens(
    user_id="user_123",
    tst_amount=Decimal("5"),
    deposit_tx_hash="0x1234567890abcdef"
)

# Credit balance
success, msg = await db_manager.credit_user_balance(
    user_id="user_123",
    amount=Decimal("500"),
    asset_type="usdt"
)
```

### 3. DepositEntityIntegration (`backend/entity/deposit_integration.py`)

Connects deposit system with autonomous entities.

**Classes:**
- `DepositApprovalRequest`: Request sent to entities
- `DepositApprovalResponse`: Entity approval with score
- `DepositEntityIntegration`: Approval orchestration
- `RiskEntityMock`: Example Risk entity
- `StrategyEntityMock`: Example Strategy entity

**Entity Responsibilities:**

| Entity | Cycle | Responsibility | Score |
|--------|-------|-----------------|-------|
| **Risk** | 3 min | Anomaly detection | 0.0-1.0 |
| **Strategy** | 2 min | Portfolio alignment | 0.0-1.0 |
| **Execution** | 1 min | Broadcast transactions | N/A |

**Example:**
```python
integration = DepositEntityIntegration()

# Register entities
risk_entity = RiskEntityMock()
strategy_entity = StrategyEntityMock()

integration.register_entity_callback(
    EntityType.RISK,
    risk_entity.evaluate_deposit
)
integration.register_entity_callback(
    EntityType.STRATEGY,
    strategy_entity.evaluate_deposit
)

# Request approval
result = await integration.request_deposit_approval(
    deposit_id="deposit_0x123",
    user_id="user_demo_001",
    amount=Decimal("500"),
    asset_type="usdt",
    chain="bsc"
)

# Returns: {
#     "approved": True,
#     "approvals": "2/2",
#     "responses": [
#         {"entity": "risk", "approved": True, "score": 0.01},
#         {"entity": "strategy", "approved": True, "score": 0.92}
#     ]
# }
```

### 4. FastAPI Endpoints (`backend/routes/deposits.py`)

REST API for deposit operations.

**Endpoints:**

#### POST `/api/v1/deposits/create`
Create new deposit entry.

**Request:**
```json
{
  "user_id": "user_12345",
  "amount": 500,
  "asset_type": "usdt",
  "chain": "bsc",
  "tx_hash": "0x1234567890abcdef"
}
```

**Response:**
```json
{
  "id": "0x1234567890abcdef",
  "user_id": "user_12345",
  "tx_hash": "0x1234567890abcdef",
  "amount": "500",
  "asset_type": "usdt",
  "chain": "bsc",
  "status": "detected",
  "created_at": "2024-01-15T10:30:00"
}
```

#### POST `/api/v1/deposits/{deposit_id}/verify`
Verify deposit and link to user wallet.

**Request:**
```json
{
  "user_id": "user_12345",
  "wallet_address": "0x578FC7311a846997dc99bF2d4C651418DcFe309A"
}
```

**Response:**
```json
{
  "status": "verified",
  "deposit_id": "0x1234567890abcdef",
  "user_id": "user_12345",
  "wallet_address": "0x578FC73...",
  "amount": "500",
  "verified_at": "2024-01-15T10:35:00"
}
```

#### POST `/api/v1/deposits/{deposit_id}/approve`
Risk entity approval for settlement.

**Request:**
```json
{
  "user_id": "user_12345",
  "risk_approved": true,
  "anomaly_score": 0.12
}
```

**Response:**
```json
{
  "status": "approved_for_settlement",
  "deposit_id": "0x1234567890abcdef",
  "amount": "500",
  "tst_reward": "5",
  "sweep_tx": "0xsweep_tx_hash",
  "signatures_required": "2-of-3 (Risk + Strategy)",
  "next_step": "Entity system collects signatures and broadcasts sweep",
  "approved_at": "2024-01-15T10:40:00"
}
```

#### GET `/api/v1/deposits/pending`
List pending deposits.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `chain` (optional): Filter by chain (bsc/polygon)

**Response:**
```json
[
  {
    "id": "0x1234567890abcdef",
    "user_id": "user_12345",
    "tx_hash": "0x1234567890abcdef",
    "amount": "500",
    "asset_type": "usdt",
    "chain": "bsc",
    "status": "approved",
    "tst_reward": "5",
    "sweep_tx_hash": "0xsweep_tx_hash",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### GET `/api/v1/deposits/history`
Get settled deposits.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `limit` (default: 50): Max results
- `offset` (default: 0): Pagination offset

**Response:**
```json
{
  "total": 42,
  "limit": 50,
  "offset": 0,
  "deposits": [
    {
      "id": "0x5678901234...",
      "user_id": "user_12345",
      "tx_hash": "0x5678901234...",
      "amount": "300",
      "asset_type": "usdt",
      "chain": "polygon",
      "status": "settled",
      "tst_reward": "3",
      "sweep_tx_hash": "0xold_sweep...",
      "created_at": "2024-01-14T15:00:00",
      "settled_at": "2024-01-14T15:45:00"
    }
  ]
}
```

#### GET `/api/v1/deposits/{deposit_id}/status`
Get deposit status.

**Response:**
```json
{
  "id": "0x1234567890abcdef",
  "status": "approved",
  "amount": "500",
  "asset_type": "usdt",
  "chain": "bsc",
  "user_id": "user_12345",
  "tst_reward": "5",
  "sweep_tx": "0xsweep_tx_hash",
  "location": "pending"
}
```

#### GET `/api/v1/deposits/stats/summary`
Get aggregated statistics.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `chain` (optional): Filter by chain

**Response:**
```json
{
  "total_deposits": 42,
  "total_value": "15423.50",
  "tst_reward_distributed": "154",
  "average_deposit": "367.23",
  "settlement_rate": 95.24,
  "pending_count": 2,
  "settled_count": 40
}
```

## Database Schema

**Transaction Model:**
```prisma
model Transaction {
  id                String    @id @default(cuid())
  wallet_id         String
  wallet            Wallet    @relation(fields: [wallet_id], references: [id])
  
  tx_hash           String    @unique  // Blockchain TX hash
  type              String    // "deposit", "sweep", "withdrawal", "trade"
  status            String    // "pending", "confirmed", "failed"
  
  amount            Decimal   // USD amount
  asset_type        String    // "usdt", "usdc", "native"
  chain             String    // "bsc", "polygon"
  
  from_address      String
  to_address        String
  
  block_number      Int?
  block_timestamp   DateTime?
  confirmed_at      DateTime?
  
  created_at        DateTime  @default(now())
  updated_at        DateTime  @updatedAt
  
  @@index([wallet_id])
  @@index([status])
  @@index([created_at])
}
```

**TST Stake Model:**
```prisma
model TSTStake {
  id                    String    @id @default(cuid())
  user_id               String
  user                  User      @relation(fields: [user_id], references: [id])
  
  amount                Decimal   // TST token amount
  status                String    // "active", "unstaking", "unstaked"
  
  total_rewards_earned  Decimal   @default(0)
  rewards_claimed       Decimal   @default(0)
  rewards_unclaimed     Decimal   @default(0)
  
  staked_at             DateTime  @default(now())
  unstaked_at           DateTime?
  
  @@index([user_id])
  @@index([status])
}
```

## Status Lifecycle

```
DETECTED
    ↓
VERIFIED (User wallet confirmed)
    ↓
APPROVED (Entity system approved)
    ↓
SWEEPING (Sweep TX in progress)
    ↓
SWEPT (Sweep confirmed on-chain)
    ↓
SETTLED (Database updated, TST awarded)
```

Or:

```
DETECTED → REJECTED (Risk entity rejected)
```

## Multi-Sig Policy

### Master Wallet (Where funds settle)
- **Address**: 0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce
- **Policy**: 2-of-3 multi-sig
- **Signers**: Risk Entity, Strategy Entity, Execution Entity
- **Threshold**: Risk + Strategy must approve

### User Wallets (Where deposits arrive)
- **Example**: 0x578FC7311a846997dc99bF2d4C651418DcFe309A
- **Policy**: Single-sig (user only via MetaMask)
- **Recovery**: Via seed phrase derivation

## TST Reward Calculation

**Formula:** 1 TST per $100 USDT

**Examples:**
| Deposit | TST Reward |
|---------|-----------|
| $50 | 0.5 |
| $100 | 1 |
| $500 | 5 |
| $1000 | 10 |

**Staking APY:** 8%

## Testing

### Test Deposit Detection
```bash
python backend/deposit/listener.py
```

### Test Entity Integration
```bash
python backend/entity/deposit_integration.py
```

### Test Database Operations
```python
# In test file
from backend.deposit.database import DepositDatabaseManager
from prisma import Prisma

db = Prisma()
await db.connect()

manager = DepositDatabaseManager(db)

# Test creating transaction record
await manager.record_deposit_transaction(...)

# Test crediting balance
success, msg = await manager.credit_user_balance(...)

# Test TST reward
success, stake = await manager.award_tst_tokens(...)
```

## Integration with FastAPI

**In `main.py`:**
```python
from fastapi import FastAPI
from backend.routes.deposits import router as deposit_router

app = FastAPI()

# Initialize deposit services (singleton)
from backend.deposit.listener import DepositListener, FundSettlement
from backend.deposit.database import DepositDatabaseManager
from backend.entity.deposit_integration import DepositEntityIntegration

listener = DepositListener({
    "bsc": os.getenv("BSC_RPC_URL"),
    "polygon": os.getenv("POLYGON_RPC_URL"),
})

settlement = FundSettlement(
    master_wallet=os.getenv("MASTER_WALLET")
)

db_manager = DepositDatabaseManager(db)

integration = DepositEntityIntegration()

# Mount routes
app.include_router(deposit_router)
```

## Security Considerations

1. **Private Keys**: Never stored plaintext
   - Derived from seed phrase
   - Stored encrypted in HSM (production)
   - Multi-sig required for master wallet

2. **Anomaly Detection**: Risk entity checks
   - First-time deposits flagged
   - Unusual amounts reviewed
   - Velocity checks (deposits per day)

3. **Compliance**: Audit trail for all operations
   - User deposits tracked
   - Entity approvals logged
   - Sweep transactions recorded
   - Settlement finality recorded

4. **Multi-Sig Enforcement**: 2-of-3 for master wallet
   - Risk must approve
   - Strategy must approve
   - Execution broadcasts only

## Future Enhancements

1. **Real Blockchain Monitoring**
   - Replace mock listener with Web3 event listeners
   - Handle blockchain reorgs (7-block confirmation)
   - Support additional chains (Arbitrum, Optimism)

2. **Advanced Anomaly Detection**
   - ML model integration
   - User behavior analysis
   - Fraud pattern library

3. **Batch Sweeps**
   - Aggregate multiple deposits
   - Reduce gas costs
   - Scheduled sweeps (hourly/daily)

4. **Withdrawal Support**
   - User redemptions from master wallet
   - Reverse sweep (master → user wallet)
   - Same multi-sig policy

5. **Cross-Chain Bridges**
   - Polygon ↔ BSC transfers
   - Consolidated master wallet
   - Unified balance tracking
