# Citadel - Wallet Architecture
## Professional Key Management System

**Status:** Phase 0 Week 3 - Foundation Architecture  
**Date:** January 30, 2026  
**Author:** Citadel Protocol  

---

## 1. Overview

Wallets are **NOT simple addresses**. They're complete systems encompassing:

```
WALLET SYSTEM
├── Key Management (generation, storage, rotation)
├── Derivation (BIP44 hierarchical paths)
├── Signing Policy (who can sign what)
├── Lifecycle Controls (create → active → rotate → recover)
└── Recovery Paths (seed backup, guardians, emergency access)
```

This aligns with:
- 🏦 How exchanges operate (custody tier)
- 🔐 How custodians manage assets (institutional grade)
- 🤖 How serious protocols work (entity-based governance)
- 🔄 How your 5-entity system governs behavior

---

## 2. Key Derivation Strategy (BIP44)

### Master Seed
```
Master Seed (24 words)
= "produce dice skin segment album section group lawn cup wisdom 
   rich frequent pledge bright cage barrel demise sell sunset 
   picnic lend post race pact"

Purpose: Single source of truth for ALL keys
Security: Never leaves HSM in production
Backup: Written on paper, stored in vault
```

### Hierarchical Derivation Paths

```
Master Seed
    ↓
Master Private Key (m)
    ↓
┌─────────────────────────────────────────────────────┐
│                                                     │
├─ m/44'/60'/0'/0/0    → MASTER_WALLET               │
│  (Consolidation vault, receives all user deposits)  │
│  Address: 0x571E52efc50055d760CEaE2446aE3B469a806279
│  Chains: BSC, Polygon                               │
│  Signing: Multi-sig (2-of-3 approval required)      │
│                                                     │
├─ m/44'/60'/0'/0/1    → USER_WALLET_1 (Alice)       │
├─ m/44'/60'/0'/0/2    → USER_WALLET_2 (Bob)         │
├─ m/44'/60'/0'/0/3    → USER_WALLET_3 (Carol)       │
│  ...                                                │
│  Addresses: Unique per user                         │
│  Chains: BSC only (primary)                         │
│  Signing: Single-sig (user only)                    │
│                                                     │
└─ m/44'/60'/0'/0/255  → SIGNING_WALLET (service)    │
   (Entity system execution, small amounts)           │
   Address: 0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce
   Chains: BSC, Polygon                               │
   Signing: Entity approval (Risk + Strategy + Exec)  │
└─────────────────────────────────────────────────────┘

Principle:
- Different path = Different purpose
- Different purpose = Different signing policy
- Different policy = Graduated trust levels
```

---

## 3. Signing Policies

### 3.1 User Wallets (m/44'/60'/0'/0/1-254)

**Single-Signature Model**

```
Transaction Flow:
  
  User initiates deposit
        ↓
  Citadel detects to-address (user wallet)
        ↓
  User signs with MetaMask (if they import seed)
        ↓
  Transaction broadcasts
        ↓
  Citadel listener confirms receipt
        ↓
  Automatic sweep to MASTER_WALLET
```

**Requirements:**
- ✅ User holds private key (never generated/stored by Citadel)
- ✅ User signs directly via MetaMask/Web3 wallet
- ✅ Citadel never sees the key
- ✅ Only for deposits (receiving transfers)

---

### 3.2 Master Wallet (m/44'/60'/0'/0/0)

**Multi-Signature Model (2-of-3)**

```
Action: Consolidate user deposits to MASTER_WALLET

Requires:
  1. Risk Entity Approval (anomaly check passes)
  2. Strategy Entity Signature (decision confirmed)
  3. Execution Entity Broadcast (actual transaction)

Flow:
  User Wallet receives $1000 USDT
        ↓
  Listener detects deposit
        ↓
  Risk Entity runs checks (is $1000 legitimate?)
        ↓
  If approved: Risk signs sweep authorization
        ↓
  Strategy Entity confirms sweep is strategically sound
        ↓
  Execution Entity broadcasts sweep transaction
        ↓
  Sweep: User Wallet → MASTER_WALLET
        ↓
  Database credit: User pocket = $1000
```

**Enforcement:**
```python
# Pseudocode: Multi-sig approval

sweep_transaction = {
    "from": user_wallet,
    "to": MASTER_WALLET,
    "amount": 1000 USDT,
    "signers_required": 2  # of 3
}

# Signature 1: Risk Entity
if risk_entity.approve(sweep_transaction):
    sig_1 = risk_entity.sign(sweep_transaction)

# Signature 2: Strategy Entity  
if strategy_entity.approve(sweep_transaction):
    sig_2 = strategy_entity.sign(sweep_transaction)

# Execute only with 2 valid signatures
if verify_signatures(sig_1, sig_2):
    broadcast_transaction(sweep_transaction)
else:
    reject_sweep()
```

---

### 3.3 Signing Wallet (m/44'/60'/0'/0/255)

**Entity-Controlled Execution**

```
Purpose: Execute strategy trades (small amounts)

Controlled By: Execution Entity
         ↓
Receives approval from:
- Risk Entity (confidence threshold met)
- Strategy Entity (decision confirmed)
- Memory Entity (historical patterns support)
         ↓
Broadcast trade to DEX
         ↓
Keep gains in MASTER_WALLET (sweep after)

Rules:
- Maximum per transaction: $1000 USDT
- Maximum per day: $10000 USDT  
- Requires all 3 entity approvals
- Risk Entity can veto (anomaly detected)
```

---

## 4. Lifecycle Controls

### 4.1 Wallet Creation (User Signup)

```
User Signup Flow:

1. User creates account via UI
   - Email verification
   - Password setup
   - Risk profile selection

2. Citadel derives unique wallet
   
   user_index = get_next_user_index()  # 1, 2, 3...
   path = f"m/44'/60'/0'/0/{user_index}"
   
   private_key = derive_from_seed(path)
   address = private_key_to_address(private_key)
   
   # Store in database (encrypted)
   wallet = {
       user_id: "user_123",
       address: address,
       path: path,
       status: "active",
       chain: "bsc",
       created_at: now()
   }

3. Show QR code to user
   "Send USDT to: 0xUSER_WALLET_ADDRESS"

4. Wallet ready to receive deposits
```

**Database Schema:**
```prisma
model Wallet {
  id              String @id @default(cuid())
  userId          String @unique
  address         String @unique      // 0xABC...
  chain           String              // "bsc", "polygon"
  derivationPath  String              // "m/44'/60'/0'/0/1"
  status          String @default("active")  // active, rotating, recovered
  createdAt       DateTime @default(now())
  rotatedAt       DateTime?
}
```

---

### 4.2 Key Rotation (Quarterly)

```
Rotation Policy: Every 90 days OR when Risk Entity flags anomaly

Trigger:
  Risk Entity detects suspicious activity
        ↓
  Rotation initiated
        ↓
  
Rotation Process:

1. Create new wallet at different path
   new_path = f"m/44'/60'/0'/0/{user_index}_v2"
   new_address = derive_from_seed(new_path)

2. Notify user
   "New deposit address: 0xNEW_ADDRESS
    Old address still works for 30 days"

3. Sweep remaining balance
   old_address → MASTER_WALLET

4. Update database
   wallet.status = "rotated"
   wallet.rotatedAt = now()
   
5. Create new wallet entry
   new_wallet = {
       user_id: user_id,
       address: new_address,
       path: new_path,
       status: "active",
       previousWallet: old_address
   }
```

---

### 4.3 Recovery (Compromise / Loss)

```
Scenario 1: User loses access to account
─────────────────────────────────────────

1. User submits recovery request
   - Email verification
   - KYC re-verification
   - Guardian approval (if set)

2. Guardian Check
   GuardianCheck {
       type: "account_recovery",
       status: "pending",
       user: user_id,
       securityLevel: "high"
   }

3. Risk Entity reviews
   - Unusual withdrawal pattern?
   - Multiple recovery attempts?
   - Flagged for manual review?

4. If approved:
   - Reset user password
   - Rotate wallet keys
   - Notify user
   - Lock account for 24h

Scenario 2: Wallet key compromised
──────────────────────────────────

1. User reports: "I think my key was exposed"

2. Risk Entity action:
   risk_entity.FLAG(wallet_id, "compromised")
        ↓
   wallet.status = "rotated"

3. Immediate rotation:
   - New wallet created
   - Old wallet marked "inactive"
   - Remaining balance swept

4. User given new address
```

---

## 5. Recovery Paths

### 5.1 Seed Backup Strategy

```
Master Seed Protection:

Location 1: Paper Backup (Physical Vault)
- 24 words written on paper
- Stored in fireproof safe
- Geographic redundancy (2 locations)

Location 2: Split Keys (Shamir Secret Sharing)
- Master seed split into 3 shares
- Each share stored separately:
  Share 1: Founder 1 + Password
  Share 2: Founder 2 + Password  
  Share 3: Secure Key Management Service
- Any 2 shares = recover entire seed
- No single person has complete seed

Location 3: Cold Storage (Hardware)
- Ledger hardware wallet
- Stored in vault
- Requires physical + digital access

Recovery: Never needed (derive from seed) unless:
- Citadel infrastructure failure
- Complete database loss
- Need to reconstruct all wallets
```

### 5.2 Guardian Approval

```
High-risk operations require guardian approval:

Operations:
✓ Wallet rotation
✓ Large withdrawals (> $100k)
✓ Account recovery
✓ Entity override (manual execution)

Guardian System:
- 2-of-3 multi-sig guardians
- Can be:
  * Legal entity
  * Insurance provider
  * Community treasury DAO
  * Decentralized governance

Guardian Check:
  GuardianCheck {
      type: "large_withdrawal",
      amount: 150000,
      user: user_123,
      status: "pending",
      approvals: 0/2,  # Need 2 of 3
      createdAt: now()
  }

Resolution:
  Guardian1.approve() → approvals = 1
  Guardian2.approve() → approvals = 2
                            ↓
                      Execute action
```

---

## 6. Integration with Entity System

### Risk Entity ↔ Wallet Lifecycle

```
Risk Entity (3-min cycle)
    ↓
Monitors wallet activity:
  - Deposit patterns
  - Withdrawal patterns
  - Anomalies vs. baseline
  - Fraud indicators
    ↓
Actions:
  
  ✓ Normal: No action
  
  ⚠ Suspicious (confidence 0.6-0.8):
    → FLAG for review
    → Notify user
    → Increase monitoring
    
  🚨 Critical (confidence > 0.9):
    → Trigger wallet rotation
    → Pause large withdrawals
    → Require guardian approval
    → Lock funds pending review
```

### Example: Anomaly Detection Triggers Rotation

```
Timeline:
────────

T0: User normal deposits $100 2x/week for 3 months
    Risk Entity baseline: $100 deposits, regular pattern

T1: Suddenly $50,000 deposit from new source
    Risk Entity anomaly score: 0.95 (critical)
        ↓
    risk_entity.flag(wallet_id, "unusual_deposit_source")
        ↓
    Guardian check triggered
        ↓
    
T2: User verifies "Yes, I received bonus payment"
    guardians_approve(check)
        ↓
    Deposit allowed, continue
    
T3: User tries to withdraw $45,000 to unknown address
    Risk Entity anomaly score: 0.98 (critical)
        ↓
    risk_entity.rotate_wallet()
        ↓
    Old wallet marked inactive
    New wallet created
    Old address gets blacklisted
    
    User notified: "New deposit address: 0xNEW...
                   Your previous address has been rotated due
                   to security concerns. No action needed."
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
```
✓ Database schema for wallets
✓ BIP44 derivation implementation
✓ Single-sig user wallet creation
✓ Deposit listener
✓ Manual sweep to MASTER_WALLET
```

### Phase 2: Automation (Weeks 3-4)
```
□ Automatic sweep (when entities approve)
□ Multi-sig signing for MASTER_WALLET
□ Key rotation policy
□ Recovery flow
```

### Phase 3: Governance (Weeks 5-6)
```
□ Guardian approval workflow
□ Risk-based triggers
□ Anomaly detection
□ Emergency override
```

### Phase 4: Custody (Weeks 7+)
```
□ Institutional tier (white-label wallets)
□ HSM integration (hardware security module)
□ Audit compliance
□ SOC 2 certification
```

---

## 8. Security Checklist

```
Key Generation:
□ Use cryptographically secure RNG
□ Never log private keys
□ Rotate seed periodically
□ Test recovery procedures quarterly

Key Storage:
□ Encrypt at rest (AES-256)
□ Encrypt in transit (TLS 1.3)
□ No keys in version control
□ No keys in logs
□ Hardware security module (production)

Signing:
□ Signature verification on every tx
□ Atomic commit (all-or-nothing)
□ Timeout protection (no hanging txs)
□ Replay attack prevention (chain ID check)

Access Control:
□ Role-based access (who can sign what)
□ Time-based locks (business hours only)
□ IP whitelisting (if centralized signing)
□ 2FA for all admin functions

Monitoring:
□ Log all key access
□ Monitor unusual signing patterns
□ Alert on failed signature attempts
□ Audit trail immutable (blockchain-backed)
```

---

## 9. FAQ

**Q: Why hierarchical derivation instead of random keys?**
A: Hierarchical derivation allows:
- Single seed = infinite wallets
- Backup one seed = backup everything
- Rotate one wallet without affecting others
- Institutional-grade custody

**Q: Why multi-sig for MASTER_WALLET?**
A: Because MASTER_WALLET holds all user funds:
- Single compromised key = all user funds at risk
- Multi-sig requires conspiracy (3 entities)
- Risk entity can veto if suspicious
- Strategy entity ensures moves are sound
- Execution entity only broadcasts approved txs

**Q: Can users export their private keys?**
A: In Phase 0 (MVP): NO
- Users deposit via wallet addresses
- Citadel holds private keys (custodial)
- Users never see private keys
- Similar to centralized exchanges

In Phase 2 (Pro tier): OPTIONAL
- Advanced users can export
- Warnings about security risks
- Only after security training

**Q: What if the seed is lost?**
A: Wallets are RECOVERED, not lost:
- All wallets are mathematically derived
- Seed is backed up (3 split shares)
- Any 2 shares = recover entire system
- No private keys lost, just access restored

---

## 10. Reference

**BIP44 Standard:**
https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki

**Related Citadel Docs:**
- [SMART_CONTRACTS.md](SMART_CONTRACTS.md) - TST & custody contracts
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Wallet tables
- [PROJECT_MANIFEST.md](PROJECT_MANIFEST.md) - System architecture
