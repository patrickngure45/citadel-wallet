"""
Citadel - TST Service
Business logic for TST access token operations
Interfaces with smart contracts and database
"""

import os
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import json
from web3 import Web3
from eth_account import Account

# Assuming Prisma ORM is available
# from prisma import Prisma


class TSTService:
    """
    Handles TST operations:
    - Lock/release TST for P2P agreements
    - Tier staking with 30-day duration
    - Entity compute quotas
    - Balance tracking
    """
    
    # TST Contract Configuration
    # These would be loaded from environment/config in production
    CONTRACT_ADDRESSES = {
        "tst": os.getenv("TST_CONTRACT_ADDRESS", "0x0000...0000"),
        "p2p_escrow": os.getenv("P2P_ESCROW_CONTRACT_ADDRESS", "0x0000...0000"),
        "access_tier_staking": os.getenv("ACCESS_TIER_STAKING_ADDRESS", "0x0000...0000"),
        "entity_compute_reserve": os.getenv("ENTITY_COMPUTE_RESERVE_ADDRESS", "0x0000...0000"),
    }
    
    # Contract ABIs (simplified - actual ABIs from deployment)
    TST_ABI = json.loads(os.getenv("TST_ABI", "[]"))
    P2P_ESCROW_ABI = json.loads(os.getenv("P2P_ESCROW_ABI", "[]"))
    ACCESS_TIER_ABI = json.loads(os.getenv("ACCESS_TIER_ABI", "[]"))
    ENTITY_COMPUTE_ABI = json.loads(os.getenv("ENTITY_COMPUTE_ABI", "[]"))
    
    # Web3 Provider
    WEB3_PROVIDER = os.getenv("WEB3_PROVIDER", "https://bsc-testnet-rpc.publicnode.com")
    
    # Tier configuration
    TIER_CONFIG = {
        1: {
            "required_tst": Decimal("5"),
            "quota_per_day": 5,
            "benefits": ["5 entity reserves/day", "Basic access tier"]
        },
        2: {
            "required_tst": Decimal("25"),
            "quota_per_day": 10,
            "benefits": ["10 entity reserves/day", "Extended compute quota", "Priority support"]
        },
        3: {
            "required_tst": Decimal("100"),
            "quota_per_day": 20,
            "benefits": ["20 entity reserves/day", "Unlimited compute quota", "Premium support", "Advanced analytics"]
        }
    }
    
    # Lock amounts for P2P agreements (tier-dependent)
    P2P_LOCK_AMOUNTS = {
        1: Decimal("10"),    # Basic tier: 10 TST
        2: Decimal("50"),    # Tier 2: 50 TST
        3: Decimal("250")    # Tier 3+: 250 TST
    }
    
    def __init__(self):
        """Initialize Web3 connection and contracts"""
        self.w3 = Web3(Web3.HTTPProvider(self.WEB3_PROVIDER))
        
        # Initialize contract instances
        if self.TST_ABI:
            self.tst_contract = self.w3.eth.contract(
                address=self.CONTRACT_ADDRESSES["tst"],
                abi=self.TST_ABI
            )
        if self.P2P_ESCROW_ABI:
            self.p2p_contract = self.w3.eth.contract(
                address=self.CONTRACT_ADDRESSES["p2p_escrow"],
                abi=self.P2P_ESCROW_ABI
            )
        if self.ACCESS_TIER_ABI:
            self.tier_contract = self.w3.eth.contract(
                address=self.CONTRACT_ADDRESSES["access_tier_staking"],
                abi=self.ACCESS_TIER_ABI
            )
        if self.ENTITY_COMPUTE_ABI:
            self.compute_contract = self.w3.eth.contract(
                address=self.CONTRACT_ADDRESSES["entity_compute_reserve"],
                abi=self.ENTITY_COMPUTE_ABI
            )
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _tst_to_wei(self, tst_amount: Decimal) -> int:
        """Convert TST (whole tokens) to wei (10^18)"""
        return int(tst_amount * Decimal(10 ** 18))
    
    def _wei_to_tst(self, wei_amount: int) -> Decimal:
        """Convert wei to TST (whole tokens)"""
        return Decimal(wei_amount) / Decimal(10 ** 18)
    
    async def get_user_tst_balance(self, user_address: str) -> Decimal:
        """
        Get user's TST balance from contract
        NOTE: In production, contracts track balances via recordLock/recordStake
        """
        try:
            # This would call: getAvailableBalance(userAddress)
            # For now, return placeholder
            return Decimal("0")
        except Exception as e:
            raise Exception(f"Failed to get TST balance: {str(e)}")
    
    def _get_tier_for_amount(self, tst_amount: Decimal) -> Optional[int]:
        """Determine which tier(s) can be purchased with given TST amount"""
        eligible_tiers = []
        for tier, config in self.TIER_CONFIG.items():
            if tst_amount >= config["required_tst"]:
                eligible_tiers.append(tier)
        return max(eligible_tiers) if eligible_tiers else None
    
    # ═══════════════════════════════════════════════════════════════
    # LOCK TST OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    async def lock_tst_for_agreement(
        self,
        user_id: str,
        amount: Decimal,
        agreement_id: str,
        duration_seconds: int,
        db
    ) -> dict:
        """
        Lock TST for P2P agreement
        
        Flow:
        1. Validate user has enough TST
        2. Call P2PAgreementEscrow.lockForAgreement()
        3. Store lock record in database
        4. Return lock details
        """
        try:
            # Validate tier-based amount requirement
            # (Simplified: in production, verify user's tier)
            
            # Convert to wei for contract call
            amount_wei = self._tst_to_wei(amount)
            lock_duration = duration_seconds
            
            # Call contract: lockForAgreement(amount, duration)
            # NOTE: In actual implementation, would call contract via Web3
            # tx_hash = await self._send_transaction(
            #     contract=self.p2p_contract,
            #     function="lockForAgreement",
            #     args=[amount_wei, lock_duration]
            # )
            
            # For MVP, generate mock contract lock ID
            contract_lock_id = f"0x{'0' * 63}1"  # Mock
            tx_hash = f"0x{'0' * 63}a"  # Mock
            
            # Calculate lock expiry
            locked_until = datetime.utcnow() + timedelta(seconds=lock_duration)
            
            # Store in database
            lock_record = {
                "userId": user_id,
                "amount": amount,
                "agreementId": agreement_id,
                "lockedUntil": locked_until.isoformat(),
                "contractLockId": contract_lock_id,
                "txHash": tx_hash,
            }
            
            # TODO: Create in database via Prisma
            # lock = await db.tst_lock.create(data=lock_record)
            
            return {
                "lock_id": f"lock_{contract_lock_id[:16]}",
                "user_id": user_id,
                "amount": amount,
                "locked_until": locked_until,
                "tx_hash": tx_hash,
                "contract_lock_id": contract_lock_id,
                "created_at": datetime.utcnow(),
            }
            
        except Exception as e:
            raise Exception(f"Failed to lock TST: {str(e)}")
    
    async def release_tst_lock(
        self,
        lock_id: str,
        user_id: str,
        db
    ) -> dict:
        """
        Release a TST lock after agreement expires or is terminated
        """
        try:
            # TODO: Fetch lock from database
            # lock = await db.tst_lock.findUnique(where={"id": lock_id})
            
            # Call contract: releaseAfterExpiry(contractLockId)
            # OR earlyTerminate(contractLockId)
            
            # For MVP, return mock response
            return {
                "lock_id": lock_id,
                "released_at": datetime.utcnow(),
                "amount_released": Decimal("10"),
                "tx_hash": f"0x{'0' * 63}b",
            }
            
        except Exception as e:
            raise Exception(f"Failed to release lock: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════
    # TIER STAKING OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    async def upgrade_access_tier(
        self,
        user_id: str,
        target_tier: int,
        strategy_id: str,
        db
    ) -> dict:
        """
        Stake TST to upgrade access tier
        
        Flow:
        1. Validate user has enough TST for tier
        2. Call AccessTierStaking.stakeForTier(tier)
        3. Store stake record in database
        4. Return tier details with benefits
        """
        try:
            # Validate tier is valid (1, 2, or 3)
            if target_tier not in self.TIER_CONFIG:
                raise ValueError(f"Invalid tier: {target_tier}")
            
            tier_config = self.TIER_CONFIG[target_tier]
            required_tst = tier_config["required_tst"]
            benefits = tier_config["benefits"]
            
            # Convert to wei
            amount_wei = self._tst_to_wei(required_tst)
            
            # Call contract: stakeForTier(tier)
            # NOTE: In actual implementation, would call contract
            # tx_hash = await self._send_transaction(
            #     contract=self.tier_contract,
            #     function="stakeForTier",
            #     args=[target_tier]
            # )
            
            # For MVP, generate mock contract stake ID
            contract_stake_id = f"0x{'0' * 63}2"  # Mock
            tx_hash = f"0x{'0' * 63}c"  # Mock
            
            # Calculate expiry (30 days)
            expires_at = datetime.utcnow() + timedelta(days=30)
            
            # Store in database
            stake_record = {
                "userId": user_id,
                "tier": target_tier,
                "amount": required_tst,
                "expiresAt": expires_at.isoformat(),
                "contractStakeId": contract_stake_id,
                "txHash": tx_hash,
                "active": True,
            }
            
            # TODO: Create in database via Prisma
            # stake = await db.tst_stake.create(data=stake_record)
            
            return {
                "stake_id": f"stake_{contract_stake_id[:16]}",
                "user_id": user_id,
                "tier": target_tier,
                "amount": required_tst,
                "expires_at": expires_at,
                "tx_hash": tx_hash,
                "contract_stake_id": contract_stake_id,
                "benefits": benefits,
                "created_at": datetime.utcnow(),
            }
            
        except Exception as e:
            raise Exception(f"Failed to upgrade tier: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════
    # ENTITY COMPUTE QUOTA OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    async def reserve_entity_quota(
        self,
        user_id: str,
        entity_type: int,
        entity_id: str,
        db
    ) -> dict:
        """
        Reserve compute quota for an entity
        
        Flow:
        1. Get user's current tier
        2. Check if quota available today
        3. Call EntityComputeReserve.reserveForEntity()
        4. Store/update quota record in database
        5. Return quota status
        """
        try:
            # Validate entity type (1, 2, or 3)
            if entity_type not in [1, 2, 3]:
                raise ValueError(f"Invalid entity type: {entity_type}")
            
            # TODO: Get user's current tier from database
            # current_tier = await self._get_active_tier(user_id, db)
            current_tier = 1  # Default tier
            
            if not current_tier:
                raise ValueError("User does not have an active tier")
            
            # Get quota allocation for tier
            quota_per_day = self.TIER_CONFIG[current_tier]["quota_per_day"]
            
            # TODO: Get/create entity access record from database
            # entity_access = await db.entityAccessTier.findUnique(
            #     where={"userId_entityType": {"userId": user_id, "entityType": entity_type}}
            # )
            
            # For MVP, create mock entity access
            entity_access = {
                "quotaPerDay": quota_per_day,
                "quotaUsedToday": 0,
                "lastResetTime": datetime.utcnow(),
            }
            
            # Check if quota available
            quota_used = entity_access.get("quotaUsedToday", 0)
            quota_remaining = quota_per_day - quota_used
            
            if quota_remaining <= 0:
                raise ValueError(f"No quota remaining for today (limit: {quota_per_day})")
            
            # Call contract: reserveForEntity(entityType, 1 unit)
            # NOTE: In actual implementation, would call contract
            # tx_hash = await self._send_transaction(
            #     contract=self.compute_contract,
            #     function="reserveForEntity",
            #     args=[entity_type]
            # )
            
            # For MVP, generate mock contract reservation ID
            contract_res_id = f"0x{'0' * 63}3"  # Mock
            tx_hash = None
            
            # Calculate reservation expiry (24 hours)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Update database
            updated_quota = {
                "quotaUsedToday": quota_used + 1,
                "lastResetTime": entity_access["lastResetTime"],
            }
            
            # TODO: Update in database via Prisma
            # updated = await db.entityAccessTier.update(
            #     where={"id": entity_access.id},
            #     data=updated_quota
            # )
            
            return {
                "reservation_id": f"res_{contract_res_id[:16]}",
                "user_id": user_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "quota_reserved": 1,
                "quota_remaining_today": quota_remaining - 1,
                "reservation_expires_at": expires_at,
                "contract_res_id": contract_res_id,
                "created_at": datetime.utcnow(),
            }
            
        except Exception as e:
            raise Exception(f"Failed to reserve quota: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════
    # INFORMATION/STATUS OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def get_tst_requirements(self, action: str) -> dict:
        """
        Get TST requirements for a specific action
        
        Actions supported:
        - lock_p2p: Lock TST for P2P agreement
        - upgrade_tier: Upgrade access tier
        - reserve_entity: Reserve entity compute quota
        """
        action_requirements = {
            "lock_p2p": {
                "action": "lock_p2p",
                "description": "Lock TST for P2P agreement execution",
                "tiers_available": [
                    {
                        "tier": 1,
                        "required_tst": self.P2P_LOCK_AMOUNTS[1],
                        "duration_days": 0,  # Dynamic per agreement
                        "benefits": ["Lock 10 TST per agreement"]
                    },
                    {
                        "tier": 2,
                        "required_tst": self.P2P_LOCK_AMOUNTS[2],
                        "duration_days": 0,
                        "benefits": ["Lock 50 TST per agreement"]
                    },
                    {
                        "tier": 3,
                        "required_tst": self.P2P_LOCK_AMOUNTS[3],
                        "duration_days": 0,
                        "benefits": ["Lock 250 TST per agreement"]
                    }
                ],
                "min_balance_required": self.P2P_LOCK_AMOUNTS[1]
            },
            "upgrade_tier": {
                "action": "upgrade_tier",
                "description": "Upgrade access tier to unlock compute quotas",
                "tiers_available": [
                    {
                        "tier": tier,
                        "required_tst": config["required_tst"],
                        "duration_days": 30,
                        "benefits": config["benefits"]
                    }
                    for tier, config in self.TIER_CONFIG.items()
                ],
                "min_balance_required": min(c["required_tst"] for c in self.TIER_CONFIG.values())
            },
            "reserve_entity": {
                "action": "reserve_entity",
                "description": "Reserve compute quota for entity (Risk, Strategy, or Memory)",
                "tiers_available": [
                    {
                        "tier": tier,
                        "required_tst": config["required_tst"],
                        "duration_days": 30,
                        "benefits": [f"Reserve {config['quota_per_day']} entities/day"]
                    }
                    for tier, config in self.TIER_CONFIG.items()
                ],
                "min_balance_required": min(c["required_tst"] for c in self.TIER_CONFIG.values())
            }
        }
        
        if action not in action_requirements:
            raise ValueError(f"Unknown action: {action}")
        
        return action_requirements[action]
    
    async def get_user_access_status(self, user_id: str, db) -> dict:
        """
        Get user's complete TST access status
        
        Includes:
        - Total balance, available, locked, staked
        - Current tier and expiry
        - Active locks
        - Active stakes
        - Entity quotas
        """
        try:
            # TODO: Fetch from database via Prisma
            # user_balance = await db.tst.getAvailableBalance(user_id)
            # active_tier = await db.tst_stake.findFirst(
            #     where={"userId": user_id, "active": True, "expiresAt": {"gt": now}}
            # )
            # locks = await db.tst_lock.findMany(
            #     where={"userId": user_id, "released": False}
            # )
            # stakes = await db.tst_stake.findMany(
            #     where={"userId": user_id, "active": True}
            # )
            # quotas = await db.entityAccessTier.findMany(
            #     where={"userId": user_id}
            # )
            
            # For MVP, return mock response
            now = datetime.utcnow()
            
            return {
                "user_id": user_id,
                "total_tst_balance": Decimal("150"),
                "available_tst": Decimal("100"),
                "locked_tst": Decimal("25"),
                "staked_tst": Decimal("25"),
                "current_tier": 2,
                "tier_expires_at": now + timedelta(days=15),
                "active_locks": [
                    {
                        "lock_id": "lock_123",
                        "amount": Decimal("25"),
                        "locked_until": now + timedelta(days=7),
                        "agreement_id": "agreement_123"
                    }
                ],
                "active_stakes": [
                    {
                        "stake_id": "stake_123",
                        "tier": 2,
                        "amount": Decimal("25"),
                        "expires_at": now + timedelta(days=15)
                    }
                ],
                "entity_quotas": [
                    {
                        "entity_type": 2,
                        "quota_today": 10,
                        "quota_used_today": 3,
                        "quota_remaining": 7,
                        "last_reset": now
                    }
                ]
            }
            
        except Exception as e:
            raise Exception(f"Failed to get access status: {str(e)}")
