"""
Citadel - TST Access Token Models
Pydantic schemas for TST API endpoints
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ═══════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════

class TierLevel(int, Enum):
    """Access tier levels"""
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class EntityType(int, Enum):
    """Entity types for compute quota"""
    RISK = 1
    STRATEGY = 2
    MEMORY = 3


# ═══════════════════════════════════════════════════════════════════
# LOCK TST REQUEST/RESPONSE
# ═══════════════════════════════════════════════════════════════════

class LockTSTRequest(BaseModel):
    """Request to lock TST for P2P agreement"""
    amount: Decimal = Field(..., gt=0, description="Amount of TST to lock (in whole tokens, not wei)")
    agreement_id: str = Field(..., description="P2P agreement ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 10,
                "agreement_id": "agreementid123"
            }
        }


class LockTSTResponse(BaseModel):
    """Response after locking TST"""
    lock_id: str = Field(..., description="Unique lock ID from database")
    user_id: str = Field(..., description="User ID")
    amount: Decimal = Field(..., description="Amount locked in TST")
    locked_until: datetime = Field(..., description="When lock expires")
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    contract_lock_id: str = Field(..., description="Lock ID from smart contract")
    created_at: datetime = Field(..., description="Record creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lock_id": "lock_abc123",
                "user_id": "user_xyz",
                "amount": 10.0,
                "locked_until": "2026-02-06T12:00:00Z",
                "tx_hash": "0x1234...abcd",
                "contract_lock_id": "0xdeadbeef...",
                "created_at": "2026-01-30T12:00:00Z"
            }
        }


# ═══════════════════════════════════════════════════════════════════
# UPGRADE TIER REQUEST/RESPONSE
# ═══════════════════════════════════════════════════════════════════

class UpgradeTierRequest(BaseModel):
    """Request to upgrade access tier"""
    tier: TierLevel = Field(..., description="Target tier level (1, 2, or 3)")
    strategy_id: str = Field(..., description="Strategy ID (for context)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tier": 2,
                "strategy_id": "strategy_xyz"
            }
        }


class TierInfo(BaseModel):
    """Information about a tier level"""
    tier: int = Field(..., description="Tier number (1, 2, or 3)")
    required_tst: Decimal = Field(..., description="TST required for this tier")
    duration_days: int = Field(default=30, description="Duration in days")
    benefits: List[str] = Field(..., description="List of benefits at this tier")


class UpgradeTierResponse(BaseModel):
    """Response after upgrading tier"""
    stake_id: str = Field(..., description="Unique stake ID from database")
    user_id: str = Field(..., description="User ID")
    tier: int = Field(..., description="Tier level (1, 2, or 3)")
    amount: Decimal = Field(..., description="Amount staked in TST")
    expires_at: datetime = Field(..., description="When tier expires (30 days from now)")
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    contract_stake_id: str = Field(..., description="Stake ID from smart contract")
    benefits: List[str] = Field(..., description="Benefits unlocked at this tier")
    created_at: datetime = Field(..., description="Record creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stake_id": "stake_abc123",
                "user_id": "user_xyz",
                "tier": 2,
                "amount": 25.0,
                "expires_at": "2026-02-29T12:00:00Z",
                "tx_hash": "0x5678...efgh",
                "contract_stake_id": "0xcafebabe...",
                "benefits": ["10 entity reserves/day", "Extended compute quota"],
                "created_at": "2026-01-30T12:00:00Z"
            }
        }


# ═══════════════════════════════════════════════════════════════════
# RESERVE COMPUTE REQUEST/RESPONSE
# ═══════════════════════════════════════════════════════════════════

class ReserveComputeRequest(BaseModel):
    """Request to reserve compute quota for entity"""
    entity_type: EntityType = Field(..., description="Entity type (1=Risk, 2=Strategy, 3=Memory)")
    entity_id: str = Field(..., description="Entity ID (risk_id, strategy_id, or memory_id)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": 2,
                "entity_id": "strategy_123"
            }
        }


class ReserveComputeResponse(BaseModel):
    """Response after reserving compute"""
    reservation_id: str = Field(..., description="Unique reservation ID from database")
    user_id: str = Field(..., description="User ID")
    entity_type: int = Field(..., description="Entity type (1=Risk, 2=Strategy, 3=Memory)")
    entity_id: str = Field(..., description="Entity ID")
    quota_reserved: int = Field(..., description="Quota units reserved")
    quota_remaining_today: int = Field(..., description="Quota remaining today after reservation")
    reservation_expires_at: datetime = Field(..., description="When this reservation expires (1 day)")
    contract_res_id: Optional[str] = Field(None, description="Reservation ID from smart contract")
    created_at: datetime = Field(..., description="Record creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reservation_id": "res_abc123",
                "user_id": "user_xyz",
                "entity_type": 2,
                "entity_id": "strategy_123",
                "quota_reserved": 1,
                "quota_remaining_today": 9,
                "reservation_expires_at": "2026-01-31T12:00:00Z",
                "contract_res_id": "0xdeadbeef...",
                "created_at": "2026-01-30T12:00:00Z"
            }
        }


# ═══════════════════════════════════════════════════════════════════
# TST REQUIREMENTS (GET)
# ═══════════════════════════════════════════════════════════════════

class ActionRequirement(BaseModel):
    """Requirements for a specific action"""
    action: str = Field(..., description="Action name")
    description: str = Field(..., description="What this action does")
    tiers_available: List[TierInfo] = Field(..., description="Available tier options")
    min_balance_required: Decimal = Field(..., description="Minimum TST balance needed")


class TSTRequirementsResponse(BaseModel):
    """Response with TST requirements for an action"""
    action: str = Field(..., description="Action being queried")
    requirements: ActionRequirement = Field(..., description="Requirements details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "upgrade_tier",
                "requirements": {
                    "action": "upgrade_tier",
                    "description": "Upgrade access tier to unlock compute quotas",
                    "tiers_available": [
                        {
                            "tier": 1,
                            "required_tst": 5.0,
                            "duration_days": 30,
                            "benefits": ["5 entity reserves/day"]
                        },
                        {
                            "tier": 2,
                            "required_tst": 25.0,
                            "duration_days": 30,
                            "benefits": ["10 entity reserves/day", "Extended compute quota"]
                        },
                        {
                            "tier": 3,
                            "required_tst": 100.0,
                            "duration_days": 30,
                            "benefits": ["20 entity reserves/day", "Unlimited compute quota"]
                        }
                    ],
                    "min_balance_required": 5.0
                }
            }
        }


# ═══════════════════════════════════════════════════════════════════
# TST ACCESS STATUS (GET)
# ═══════════════════════════════════════════════════════════════════

class ActiveLock(BaseModel):
    """Information about an active lock"""
    lock_id: str = Field(..., description="Lock ID")
    amount: Decimal = Field(..., description="Amount locked in TST")
    locked_until: datetime = Field(..., description="When lock expires")
    agreement_id: Optional[str] = Field(None, description="Associated agreement ID")


class ActiveStake(BaseModel):
    """Information about an active stake"""
    stake_id: str = Field(..., description="Stake ID")
    tier: int = Field(..., description="Tier level")
    amount: Decimal = Field(..., description="Amount staked in TST")
    expires_at: datetime = Field(..., description="When stake expires")


class EntityQuota(BaseModel):
    """Information about entity quota status"""
    entity_type: int = Field(..., description="Entity type (1=Risk, 2=Strategy, 3=Memory)")
    quota_today: int = Field(..., description="Total quota available today")
    quota_used_today: int = Field(..., description="Quota used today")
    quota_remaining: int = Field(..., description="Quota remaining today")
    last_reset: datetime = Field(..., description="Last time quota was reset")


class TSTAccessResponse(BaseModel):
    """Response with user's TST access status"""
    user_id: str = Field(..., description="User ID")
    total_tst_balance: Decimal = Field(..., description="Total TST balance")
    available_tst: Decimal = Field(..., description="Available TST (not locked/staked)")
    locked_tst: Decimal = Field(..., description="Total TST locked")
    staked_tst: Decimal = Field(..., description="Total TST staked")
    current_tier: Optional[int] = Field(None, description="Currently active tier (1, 2, 3, or null)")
    tier_expires_at: Optional[datetime] = Field(None, description="When current tier expires")
    active_locks: List[ActiveLock] = Field(default_factory=list, description="List of active locks")
    active_stakes: List[ActiveStake] = Field(default_factory=list, description="List of active stakes")
    entity_quotas: List[EntityQuota] = Field(default_factory=list, description="Quota status for each entity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_xyz",
                "total_tst_balance": 150.0,
                "available_tst": 100.0,
                "locked_tst": 25.0,
                "staked_tst": 25.0,
                "current_tier": 2,
                "tier_expires_at": "2026-02-29T12:00:00Z",
                "active_locks": [
                    {
                        "lock_id": "lock_123",
                        "amount": 25.0,
                        "locked_until": "2026-02-06T12:00:00Z",
                        "agreement_id": "agreement_123"
                    }
                ],
                "active_stakes": [
                    {
                        "stake_id": "stake_123",
                        "tier": 2,
                        "amount": 25.0,
                        "expires_at": "2026-02-29T12:00:00Z"
                    }
                ],
                "entity_quotas": [
                    {
                        "entity_type": 2,
                        "quota_today": 10,
                        "quota_used_today": 3,
                        "quota_remaining": 7,
                        "last_reset": "2026-01-30T00:00:00Z"
                    }
                ]
            }
        }


# ═══════════════════════════════════════════════════════════════════
# ERROR RESPONSES
# ═══════════════════════════════════════════════════════════════════

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Error description")
    details: Optional[str] = Field(None, description="Additional details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "insufficient_balance",
                "message": "User does not have enough TST balance",
                "details": "Required: 25 TST, Available: 15 TST"
            }
        }
