# Smart Contracts Specification
## Solidity 0.8.19 - TradeSynapse Protocol

**Brand:** Citadel | **Protocol:** TradeSynapse  
**Solidity Version:** 0.8.19  
**EVM Chains:** BSC, Polygon, Tron (adapted)  
**Status:** Phase 0 Week 2 (Specifications)  
**Last Updated:** January 30, 2026

---

## Overview

**Total Contracts:** 5  
**Audit Status:** Ready for professional audit (Phase 1)  
**Security:** Multi-sig, time-locks, pausable  
**Governance:** DAO-ready (Phase 2)

---

## 1. TST TOKEN CONTRACT (ERC-20 + Staking)

**File:** `contracts/TST.sol`  
**Type:** ERC-20 with staking mechanics  
**Networks:** BSC (primary), Polygon (secondary)

### Key Features

```
Total Supply:    1,000,000 TST
Decimals:        18
Initial Mint:    Treasury (400k), Team (200k), Investors (150k), Community (250k)
```

### Contract Specification

**State Variables:**
```solidity
- name: "TradeSynapse Token"
- symbol: "TST"
- totalSupply: 1,000,000e18
- balanceOf: mapping(address => uint256)
- allowance: mapping(address => mapping(address => uint256))
- stakingRegistry: mapping(address => Stake[])
- stakingApy: 8% (800 basis points)
```

**Core Functions:**

```solidity
// Standard ERC-20
function transfer(address to, uint256 amount) external returns (bool)
function transferFrom(address from, address to, uint256 amount) external returns (bool)
function approve(address spender, uint256 amount) external returns (bool)
function balanceOf(address account) external view returns (uint256)

// Staking (Yield Generation)
function stake(uint256 amount, uint256 lockDays) external payable
  - Locks TST tokens for staking period
  - Emits Staked(user, amount, lockDays)
  - Calculates annual rewards: amount * (8% / 365) * lockDays

function getStakingRewards(address user) external view returns (uint256)
  - Returns unclaimed staking rewards
  - Based on time held + APY rate

function claimStakingRewards() external
  - Claims accumulated TST rewards
  - Transfers from reward pool to user
  - Resets claimTime

function unstake(uint256 stakeId) external
  - Unlock staked tokens after lock period expires
  - Transfer principal + accumulated rewards
  - Requires: lockPeriod has ended

function emergencyUnstake(uint256 stakeId) external
  - Unstake before lock period (penalty: 10% of principal)
  - Returns: 90% principal + accumulated rewards - penalty
  - Emits EmergencyUnstake event

// Airdrop Distribution
function claimAirdrop() external
  - Each user gets 1,000 TST airdrop
  - One-time claim per address
  - Requires: not already claimed, valid user address
  - Emits AirdropClaimed(user, 1000e18)

// Owner Functions
function mint(address to, uint256 amount) external onlyOwner
  - Mint new TST (governance only)
  - Max: 10% of current supply per mint

function burn(uint256 amount) external
  - Burn TST tokens (deflationary)
  - Emits Burn(msg.sender, amount)

function setStakingApy(uint256 newApy) external onlyOwner
  - Adjust staking APY (governance decision)
  - Emits StakingApyUpdated(newApy)
```

### Staking Mechanics

**Struct:**
```solidity
struct Stake {
  uint256 amount;              // Staked amount
  uint256 stakedAt;            // Timestamp
  uint256 lockDuration;        // In seconds
  uint256 unlocksAt;           // When unlocking allowed
  uint256 rewardsClaimed;      // Total rewards claimed
  bool isActive;               // Still staked?
}
```

**Example Calculation:**
```
User stakes: 5,000 TST
Lock period: 365 days
APY: 8%

Annual reward: 5,000 * 0.08 = 400 TST
Daily reward: 400 / 365 = 1.096 TST/day

After 180 days (half-locked):
Rewards earned: 1.096 * 180 = 197.12 TST

User can claim rewards anytime (doesn't break lock)
```

### Security Considerations

- ✅ No reentrancy (single function execution)
- ✅ Integer overflow protected (Solidity 0.8.19+)
- ✅ Pausable in emergency
- ✅ Owner functions time-locked (48 hours)
- ✅ Reward pool funded upfront (no edge case)

---

## 2. ESCROW CONTRACT (Multi-Sig P2P)

**File:** `contracts/Escrow.sol`  
**Type:** Multi-signature escrow for P2P lending  
**Standard:** 2-of-3 multi-sig (User, Lender, Arbitrator)

### Purpose

Securely hold funds in P2P lending agreements:
- Lender deposits capital
- Borrower receives capital
- Time-locked release on maturity
- Dispute resolution with arbitrator

### Contract Specification

**State Variables:**
```solidity
- escrowAgreements: mapping(uint256 => Agreement)
- signatories: mapping(uint256 => address[3]) // [user, lender, arbitrator]
- approvals: mapping(uint256 => mapping(address => bool))
- holdingAmount: mapping(address => uint256) // Balance held in contract
```

**Core Agreement Struct:**
```solidity
struct Agreement {
  uint256 agreementId;
  address user;               // Borrower
  address lender;             // Lender
  address arbitrator;         // Dispute resolver
  
  uint256 principal;          // Amount being lent
  uint256 interestRate;       // % (e.g., 500 = 5.00%)
  uint256 maturityDate;       // When funds should be released
  
  bool isFunded;              // Lender has deposited
  uint256 fundedAt;           // Timestamp of funding
  
  bool isSettled;             // Borrower has repaid
  uint256 settledAt;          // Timestamp of settlement
  
  bool isDisputed;            // Under dispute?
  string disputeReason;       // Why disputed?
  
  uint256 releaseApprovals;   // Count of signed approvals
}
```

### Contract Functions

**Lender (Funding):**
```solidity
function createAgreement(
  address borrower,
  address arbitrator,
  uint256 principal,
  uint256 interestRate,
  uint256 maturityDays
) external returns (uint256 agreementId)
  - Creates new escrow agreement
  - Emits AgreementCreated(agreementId, borrower, principal)

function fundAgreement(uint256 agreementId) external payable
  - Lender deposits principal amount
  - Transfers funds to escrow contract
  - Emits AgreementFunded(agreementId, principal, fundedAt)
  - Requires: caller is lender, amount correct
```

**Borrower (Repayment):**
```solidity
function repayAgreement(uint256 agreementId) external payable
  - Borrower deposits principal + interest
  - Requires: isFunded == true, now <= maturityDate
  - Auto-releases funds if both sides agree
  - Emits RepaymentReceived(agreementId, totalAmount)
```

**Arbitration (Dispute):**
```solidity
function initiateDispute(uint256 agreementId, string reason) external
  - Any party can initiate dispute
  - Freezes agreement funds (no release until resolved)
  - Requires: arbitrator is notified
  - Emits DisputeInitiated(agreementId, reason)

function resolveDispute(uint256 agreementId, bool favorsLender) external onlyArbitrator
  - Arbitrator resolves dispute
  - If favorsLender: return principal + interest to lender
  - If favorsBorrower: return principal to borrower
  - Takes 5% fee from total amount
  - Emits DisputeResolved(agreementId, favorsLender)
```

**Automatic Release:**
```solidity
function autoReleaseOnMaturity(uint256 agreementId) external
  - Called by anyone after maturityDate
  - Requires: repayment received
  - Transfers principal + interest to lender
  - Releases escrowed funds
  - Emits AgreementSettled(agreementId)
```

### Security Safeguards

- ✅ Multi-sig approval (requires 2-of-3 signatures)
- ✅ Time-locked release (no early withdrawal)
- ✅ Dispute mechanism (arbitrator mediates)
- ✅ No reentrancy (CEI pattern)
- ✅ Upgradeable (proxy pattern, Phase 2)

---

## 3. STAKING REWARDS POOL

**File:** `contracts/StakingRewards.sol`  
**Type:** Reward distribution contract  
**Purpose:** Manage 8% APY reward payouts for staked TST

### Key Features

**Funding:**
- Rewards funded upfront (1-year supply)
- 1,000,000 TST * 8% = 80,000 TST/year
- Stored in contract (no liquidity risk)

**Distribution:**
```
Daily distribution: 80,000 / 365 = 219.18 TST/day
Per staker share: (user_staked / total_staked) * daily_amount
```

**Contract Functions:**

```solidity
function fundRewardPool(uint256 amount) external
  - Owner funds the reward pool
  - Requires: sufficient TST balance
  - Emits PoolFunded(amount)

function distributeRewards() external (called daily by bot)
  - Distributes daily rewards to all active stakers
  - Updates reward balances
  - Emits RewardsDistributed(totalAmount, stakerCount)

function claimRewards(address staker) external
  - Staker claims their accumulated rewards
  - Transfers from pool to staker wallet
  - Emits RewardsClaimed(staker, amount)

function getRewardBalance(address staker) external view returns (uint256)
  - Returns unclaimed rewards for a staker
  - Calculated: (staked_amount / total_staked) * accrued_rewards
```

---

## 4. ROUTER CONTRACT (Cross-Chain)

**File:** `contracts/Router.sol`  
**Type:** Cross-chain liquidity routing  
**Purpose:** Route capital across BSC, Polygon, Tron for best execution  
**Status:** Phase 2 (Specs only)

### High-Level Concept

```
User's $10K USDT on BSC
  → Router checks liquidity on:
    - BSC: 2.1% spread
    - Polygon: 1.9% spread ← BEST
    - Tron: 2.3% spread
  → Routes trade to Polygon
  → Bridges profit back to BSC
  → Net savings: 0.2% = $20
```

### Contract Functions (Phase 2)

```solidity
function findBestRoute(
  address token,
  uint256 amount,
  address[] memory chains
) external view returns (Route memory)
  - Checks DEX liquidity on each chain
  - Calculates execution price & slippage
  - Returns best route

function executeRouteSwap(
  Route memory route,
  uint256 minOutput
) external
  - Executes swap on selected chain
  - Uses approved bridge for cross-chain transfer
  - Emits RouteExecuted(chain, amount, output)
```

---

## 5. GOVERNANCE TOKEN (PHASE 2)

**File:** `contracts/Governance.sol`  
**Type:** DAO governance  
**Purpose:** Community voting on protocol changes  
**Status:** Phase 2 Implementation

### Features (Planned)

- Snapshot-based voting (read balances at block height)
- Proposal system (create, vote, execute)
- Quorum requirements (20% of supply)
- Time-locks on executed proposals (48 hours)

---

## Deployment Strategy

### Phase 1 (Weeks 3-4)

**Step 1: Local Testing**
```bash
# Hardhat environment
npx hardhat test

# Test coverage
npx hardhat coverage
```

**Step 2: Testnet Deployment**
```bash
# Deploy to BSC Testnet
npx hardhat run scripts/deploy.js --network bsc-testnet

# Verify on Etherscan
npx hardhat verify --network bsc-testnet <CONTRACT_ADDRESS>
```

**Step 3: Mainnet Deployment**
```bash
# BSC Mainnet
npx hardhat run scripts/deploy.js --network bsc

# Polygon Mainnet
npx hardhat run scripts/deploy.js --network polygon
```

### Deployment Order
1. TST Token
2. StakingRewards (fund with 80k TST)
3. Escrow
4. Router (Phase 2)
5. Governance (Phase 2)

---

## Security Audit Checklist

### Before Phase 1 Code Review

- [ ] All contracts use OpenZeppelin standards
- [ ] No known vulnerabilities (checked vs. Slither)
- [ ] All external calls use CEI pattern
- [ ] Integer overflow protected (Solidity 0.8.19+)
- [ ] Reentrancy guards on state-changing functions
- [ ] Owner functions time-locked (48h)
- [ ] Emergency pause functionality
- [ ] Event logging for all state changes
- [ ] No hard-coded addresses (use constructor)
- [ ] Gas optimization (storage layout, batch operations)

### Professional Audit (Phase 1, Budget: $30-50K)

**Recommended Auditors:**
- OpenZeppelin (best, $50K+)
- Trail of Bits ($30-50K)
- Consensys Diligence ($40-60K)
- Certora (formal verification, $20-30K)

**Audit Scope:**
1. Contract logic correctness
2. Security vulnerabilities (OWASP top 10)
3. Gas optimization
4. Standards compliance (ERC-20, etc.)
5. Integer math safety
6. Access control

**Timeline:**
- Week 1: Audit firm reviews code
- Week 2: Reports findings
- Week 3: Team fixes issues
- Week 4: Reaudit confirmations
- Week 5: Final report, launch ready

---

## Contract Interactions Diagram

```
User → TST Token
         ├─ transfer (buy/sell)
         └─ stake (8% APY)
              ↓
         StakingRewards
              └─ claimRewards

Lender → Escrow
         ├─ fundAgreement
         └─ repayAgreement
              ↓
         User (Borrower)
         Arbitrator (Dispute)

Router (Phase 2)
  ├─ findBestRoute (all chains)
  └─ executeRouteSwap
       ├─ BSC DEX
       ├─ Polygon DEX
       └─ Tron DEX
```

---

## Test Coverage

### Unit Tests (Hardhat)

**TST Token Tests:**
```
✓ Transfer tokens
✓ Stake and claim rewards
✓ Airdrop distribution
✓ Emergency unstake (with penalty)
✓ Owner functions (mint, burn, setAPY)
✓ Reverts on invalid amounts
✓ Reverts on unauthorized access
```

**Escrow Tests:**
```
✓ Create agreement
✓ Fund agreement
✓ Repay agreement
✓ Auto-release on maturity
✓ Initiate and resolve dispute
✓ Multi-sig approval flow
✓ Time-locked release
✓ Reverts on invalid state
```

**StakingRewards Tests:**
```
✓ Fund pool
✓ Distribute daily rewards
✓ Claim rewards
✓ Verify APY calculations
✓ Handle multiple stakers
✓ Prevent over-distribution
```

### Integration Tests

```
✓ End-to-end: stake → earn rewards → claim
✓ End-to-end: create loan → fund → repay → settle
✓ Cross-chain routing (mock)
✓ Multi-user scenarios
✓ Stress test (1000+ users)
```

---

## Gas Optimization

### Target Gas Costs

| Function | Target Gas | Actual | Status |
|----------|-----------|--------|--------|
| transfer | 65,000 | TBD | Phase 1 |
| stake | 120,000 | TBD | Phase 1 |
| claimRewards | 95,000 | TBD | Phase 1 |
| fundAgreement | 150,000 | TBD | Phase 1 |

### Optimization Strategies

1. **Storage Layout**
   - Pack variables efficiently (reduce SSTORE)
   - Group related uint256 together

2. **Batch Operations**
   - Distribute rewards in batches
   - Prevent individual loops

3. **Read-Only Functions**
   - Use `view` functions (no gas)
   - Pre-compute values when possible

4. **Upgrade Path**
   - Proxy pattern allows optimization improvements
   - No need to redeploy logic, only update

---

## Compliance & Legal

### Token Classification
- **TST is:** Utility token (governance, staking, access)
- **TST is NOT:** Security (no dividend rights)

### Regulatory Considerations
- KYC/AML compliance (user level)
- Geographic restrictions (OFAC list checks)
- Staking rewards disclosure (tax implications)
- Audit trail immutable (7-year retention)

---

## File Structure

```
contracts/
├── TST.sol                 # ERC-20 + Staking
├── Escrow.sol              # Multi-sig P2P
├── StakingRewards.sol      # APY Distribution
├── Router.sol              # Cross-chain (Phase 2)
├── Governance.sol          # DAO (Phase 2)
└── interfaces/
    ├── IERC20.sol
    ├── IStaking.sol
    └── IEscrow.sol

scripts/
├── deploy.js               # Deployment script
├── verify.js               # Etherscan verification
└── fund.js                 # Fund reward pool

test/
├── TST.test.js
├── Escrow.test.js
├── StakingRewards.test.js
└── integration.test.js
```

---

**Status:** Specifications Complete  
**Next:** Phase 1 - Implement Solidity Code (Weeks 3-4)  
**Estimated Implementation Time:** 2 weeks (with audit)
