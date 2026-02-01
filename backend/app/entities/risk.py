from typing import List
from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, RiskOutput, RiskRule

class RiskEntity(BaseEntity):
    async def process(self, record: HearingRecord) -> HearingRecord:
        verdict = "APPROVE"
        blockers = []
        rules_checked = []
        
        # 1. Extract the facts
        perceived_amount = 0.0
        detected_token = "ETH" # Default
        recipient = None
        
        for fact in record.perception.facts:
            if fact.key == "detected_amount": perceived_amount = float(fact.value)
            if fact.key == "detected_token": detected_token = fact.value
            if fact.key == "detected_recipient": recipient = fact.value
        
        # Rule 1: Global Sanity Cap (The "Fat Finger" preventer)
        # No transaction should ever exceed 1,000,000 units of anything effectively
        GLOBAL_MAX = 1000000.0
        passed_sanity = perceived_amount <= GLOBAL_MAX
        
        rules_checked.append(RiskRule(
            rule_id="RISK-001-GLOBAL-SANITY",
            passed=passed_sanity,
            reason=f"Amount {perceived_amount} <= {GLOBAL_MAX}",
            severity="CRITICAL"
        ))
        
        if not passed_sanity:
            verdict = "VETO"
            blockers.append("Transaction exceeds global sanity limits.")

        # Rule 2: Asset-Specific Velocity Limits
        # "The Fortress": Different walls for different assets
        ASSET_LIMITS = {
            "ETH": 5.0,     # Max 5 ETH per tx
            "BNB": 20.0,    # Max 20 BNB
            "BTC": 0.5,     # Max 0.5 BTC
            "USDT": 5000.0, # Max $5k stable
            "USDC": 5000.0,
            "TST": 1000.0   # Mock token
        }
        
        limit = ASSET_LIMITS.get(detected_token, 100.0) # Conservative default for unknown tokens
        passed_velocity = perceived_amount <= limit
        
        rules_checked.append(RiskRule(
            rule_id=f"RISK-002-LIMIT-{detected_token}",
            passed=passed_velocity,
            reason=f"Amount {perceived_amount} {detected_token} <= {limit} {detected_token}",
            severity="CRITICAL"
        ))
        
        if not passed_velocity:
            verdict = "VETO"
            blockers.append(f"Exceeds {detected_token} safety limit of {limit}.")

        # Rule 3: Address Whitelist (The "Moat")
        # Only allow high-value transfers to known addresses
        TRUSTED_ADDRESSES = [
            "0x571E52efc50055d760CEaE2446aE3B469a806279", # Citadel Admin
            "0x70997970C51812dc3A010C7d01b50e0d17dc79C8", # Alice (Hardhat #1)
            "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC", # Bob (Hardhat #2)
            "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce", # External Wallet (Netflix/Corporate) ✅ ADDED
        ]
        
        # Shield Mode: Strict Allowlist
        # If recipient is NOT in trusted list, we BLOCK it unless "OVERRIDE" is in the command
        passed_address = True
        addr_reason = "Recipient is verified."
        
        if recipient:
            is_trusted = recipient.lower() in [a.lower() for a in TRUSTED_ADDRESSES]
            has_override = "OVERRIDE" in record.intent.upper() or "CONFIRM" in record.intent.upper()
            
            if not is_trusted:
                if has_override:
                    addr_reason = "Unknown recipient allowed via Manual Override."
                else:
                    passed_address = False
                    addr_reason = "SHIELD ACTIVE: Recipient not in Allowlist. Add 'OVERRIDE' to proceed."

        rules_checked.append(RiskRule(
            rule_id="RISK-003-SHIELD-PROTOCOL",
            passed=passed_address,
            reason=addr_reason,
            severity="CRITICAL"
        ))
        
        if not passed_address:
            # SHIELD BLOCK
            verdict = "VETO"
            blockers.append(addr_reason)

        record.risk = RiskOutput(
            verdict=verdict,
            rules_checked=rules_checked,
            blockers=blockers
        )
        return record
