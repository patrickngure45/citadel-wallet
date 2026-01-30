# TST Smart Contracts - Deployment & Integration

**Status:** Week 2, Day 3 - Ready for Testnet Deployment

---

## Deployed Contracts

### BSC Testnet (Chain ID: 97)

| Contract | Address | Status |
|----------|---------|--------|
| TST Token | `0x[pending]` | Ready |
| P2PAgreementEscrow | `0x[pending]` | Ready |
| AccessTierStaking | `0x[pending]` | Ready |
| EntityComputeReserve | `0x[pending]` | Ready |

### Deployment Details

- **Network:** BSC Testnet
- **Deployer:** `0x[account address]`
- **Deployment Time:** January 30, 2026
- **Total Gas:** ~7.8M gas (~$30-50 USD at 3 gwei)

---

## Contract ABIs & Integration

### 1. TST Token (`TST.sol`)

```solidity
// Key Functions
function balanceOf(address account) external view returns (uint256)
function lockedBalance(address account) external view returns (uint256)
function stakedBalance(address account) external view returns (uint256)
function recordLock(uint256 amount, bytes32 lockId) external
function releaseLock(uint256 amount, bytes32 lockId) external
function recordStake(uint256 amount, uint8 tier) external
function recordUnstake(uint256 amount) external
function getAvailableBalance(address account) external view returns (uint256)
function hasAvailableBalance(address account, uint256 amount) external view returns (bool)
```

**Events:**
- `TokensLocked(address indexed user, uint256 amount, bytes32 indexed lockId)`
- `TokensReleased(address indexed user, uint256 amount, bytes32 indexed lockId)`
- `TokensStaked(address indexed user, uint256 amount, uint8 tier)`
- `TokensUnstaked(address indexed user, uint256 amount)`

---

### 2. P2P Agreement Escrow (`P2PAgreementEscrow.sol`)

```solidity
// Key Functions
function lockForAgreement(
  uint256 amount,
  uint256 duration,
  string memory agreementId
) external returns (bytes32)

function releaseAfterExpiry(bytes32 lockId) external

function earlyTerminate(bytes32 lockId) external

function isLocked(bytes32 lockId) external view returns (bool)

function getLock(bytes32 lockId) external view returns (Lock memory)

function getLocksByUser(address user) external view returns (bytes32[] memory)
```

**Events:**
- `AgreementLocked(bytes32 indexed lockId, address indexed user, uint256 amount, string agreementId, uint256 lockedUntil)`
- `AgreementReleased(bytes32 indexed lockId, address indexed user, uint256 amount)`
- `AgreementTerminated(bytes32 indexed lockId, address indexed user, uint256 amountReturned)`

**Lock Structure:**
```solidity
struct Lock {
  address user;
  uint256 amount;
  uint256 lockedUntil;
  string agreementId;
  bool released;
}
```

---

### 3. Access Tier Staking (`AccessTierStaking.sol`)

```solidity
// Key Functions
function stakeForTier(uint8 tier) external returns (bytes32)

function unstake(bytes32 stakeId) external

function hasActiveTier(address user, uint8 tier) external view returns (bool)

function getHighestActiveTier(address user) external view returns (uint8)

function getTierAmount(uint8 tier) external view returns (uint256)

function getStakesByUser(address user) external view returns (bytes32[] memory)
```

**Events:**
- `Staked(bytes32 indexed stakeId, address indexed user, uint256 amount, uint8 tier, uint256 expiresAt)`
- `Unstaked(bytes32 indexed stakeId, address indexed user, uint256 amount)`

**Tier Amounts:**
- Tier 1: 5 TST (5 * 10^18)
- Tier 2: 25 TST (25 * 10^18)
- Tier 3: 100 TST (100 * 10^18)

**Duration:** 30 days (fixed, non-perpetual)

---

### 4. Entity Compute Reserve (`EntityComputeReserve.sol`)

```solidity
// Key Functions
function reserveForEntity(uint8 entity) external returns (bytes32)

function getQuotaRemaining(
  address user,
  uint8 entity,
  uint8 tier
) external view returns (uint256)

function consumeQuota(
  address user,
  uint8 entity,
  uint8 tier,
  uint256 amount
) external

function endReservation(bytes32 reservationId) external

function getReservationsByUser(address user) external view returns (bytes32[] memory)

function getDailyQuota(uint8 entity, uint8 tier) external view returns (uint256)
```

**Events:**
- `ComputeReserved(bytes32 indexed reservationId, address indexed user, uint8 entity, uint256 amount, uint256 expiresAt)`
- `ReservationEnded(bytes32 indexed reservationId, address indexed user)`
- `QuotaConsumed(address indexed user, uint8 entity, uint256 amount)`
- `QuotaReset(address indexed user, uint8 entity)`

**Entity Types:**
- `ENTITY_RISK = 1`
- `ENTITY_STRATEGY = 2`
- `ENTITY_MEMORY = 3`

**Daily Quotas:**

| Entity | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|--------|--------|--------|--------|--------|
| Risk | 1 | 3 | 10 | 1000 |
| Strategy | 4 | 12 | 28 | 1000 |
| Memory | 2 | 7 | 28 | 1000 |

---

## API Integration Points

### Backend Initialization

```python
from web3 import Web3
import json

# Load contract ABIs
with open('contract-abis.json') as f:
    abis = json.load(f)

# Connect to BSC Testnet
w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-1.binance.org:8545'))

# Load contracts
tst = w3.eth.contract(address=TST_ADDRESS, abi=abis['TST'])
escrow = w3.eth.contract(address=ESCROW_ADDRESS, abi=abis['P2PAgreementEscrow'])
staking = w3.eth.contract(address=STAKING_ADDRESS, abi=abis['AccessTierStaking'])
reserve = w3.eth.contract(address=RESERVE_ADDRESS, abi=abis['EntityComputeReserve'])
```

### Tier Checking

```python
async def get_user_tier(user_address: str) -> int:
    """Get user's highest active tier"""
    tier = await staking.functions.getHighestActiveTier(user_address).call()
    return tier  # 0 (none), 1, 2, or 3
```

### Quota Checking

```python
async def check_entity_quota(
    user_address: str,
    entity_type: int,  # 1=Risk, 2=Strategy, 3=Memory
    tier: int
) -> int:
    """Check remaining quota for entity today"""
    remaining = await reserve.functions.getQuotaRemaining(
        user_address,
        entity_type,
        tier
    ).call()
    return remaining
```

### Consuming Quota

```python
async def consume_entity_quota(
    user_address: str,
    entity_type: int,
    tier: int,
    amount: int = 1
):
    """Consume quota after entity execution (backend only)"""
    tx = await reserve.functions.consumeQuota(
        user_address,
        entity_type,
        tier,
        amount
    ).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    return receipt
```

---

## Testing Checklist

### Unit Tests (Automated)

- [x] TST deployment and initialization
- [x] Locking and releasing tokens
- [x] Staking for tiers
- [x] Tier requirements enforcement
- [x] Quota allocation and consumption
- [x] Daily quota reset
- [x] Early termination (no penalties)
- [x] Transfer restrictions

### Integration Tests (Manual)

- [ ] Lock TST for agreement → release after duration
- [ ] Stake TST → wait 30 days → unstake
- [ ] Consume quota → verify remaining → reset after 24h
- [ ] Multiple users with different tiers
- [ ] Concurrent operations (locks + stakes)
- [ ] Edge cases (zero amounts, invalid tiers)

### Security Verification

- [ ] No transfer capability (verify transfer blocked)
- [ ] No approve capability
- [ ] No yield/minting (review code)
- [ ] Correct balance calculations
- [ ] Proper event emission

---

## Gas Cost Estimation

### Deployment
- TST: ~2.5M gas
- Escrow: ~1.8M gas
- Staking: ~1.5M gas
- Reserve: ~2.0M gas
- **Total:** ~7.8M gas

### Operations (per action)
- Lock agreement: ~80k gas (~$0.30 @ 3 gwei)
- Stake tier: ~90k gas (~$0.35 @ 3 gwei)
- Consume quota: ~70k gas (~$0.25 @ 3 gwei)
- Release lock: ~75k gas (~$0.28 @ 3 gwei)
- Unstake: ~85k gas (~$0.32 @ 3 gwei)

**Budget:** <$5 per action ✅

---

## Production Deployment Checklist

### Before Mainnet

- [ ] Audit: Security review complete
- [ ] Gas optimization: All functions optimized
- [ ] Test coverage: 100% of scenarios
- [ ] Verification: All functions verified on Etherscan
- [ ] Documentation: ABIs and integration guide complete
- [ ] Team: All stakeholders reviewed and approved
- [ ] Frozen narrative: No yield anywhere
- [ ] Go/no-go decision: Executive approval

### Phase Timeline

**Phase 1 (Current):**
- Deploy to testnet
- Internal testing only
- Zero external announcement

**Phase 2 (Weeks 7-12):**
- Deploy to mainnet
- Technical documentation published
- Selective developer access

**Phase 3 (Month 4+):**
- Public documentation
- Selective institutional access
- Public ecosystem integration

---

## Emergency Procedures

### If Contract Needs Pause

Current implementation does NOT have pause functionality (intentional).
To halt operations:
1. Revoke approvals (not applicable - no transfers)
2. Stop API calls to contract
3. Notify users

### If Lock Expires Prematurely

Users can manually call `releaseAfterExpiry()` if system fails.

### If Quota Resets Fail

Users can request manual reset through support.
Backend can call `consumeQuota()` to verify current state.

---

## Support & Documentation

**Key Documents:**
- `SMART_CONTRACTS_TST_ACCESS_MODEL.md` - Detailed specifications
- `TST_NARRATIVE_FROZEN.md` - Constitutional rules
- `TST_FRICTION_MECHANICS.md` - User-facing mechanics
- `PHASE1_WEEK2_ROADMAP_REVISED.md` - Implementation timeline

**External Resources:**
- BSC Testnet Faucet: https://testnet.binance.org/faucet-smart
- Etherscan Testnet: https://testnet.bscscan.com/
- Hardhat Documentation: https://hardhat.org/docs

---

**Status:** Ready for Day 3 Testnet Deployment ✅
