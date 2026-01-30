"""
Citadel - TST API Endpoints
REST API for TST access token operations
Implements 5 core endpoints for Phase 1 Week 2
"""

from fastapi import APIRouter, HTTPException, Depends, Path
from fastapi.responses import JSONResponse
from typing import Optional
from decimal import Decimal

# Import models and services
from backend.models.tst import (
    LockTSTRequest, LockTSTResponse,
    UpgradeTierRequest, UpgradeTierResponse,
    ReserveComputeRequest, ReserveComputeResponse,
    TSTRequirementsResponse, ActionRequirement, TierInfo,
    TSTAccessResponse, ActiveLock, ActiveStake, EntityQuota,
    ErrorResponse, EntityType, TierLevel
)
from backend.services.tst_service import TSTService

# Initialize router and service
router = APIRouter(prefix="/api/v1", tags=["TST Access Token"])
tst_service = TSTService()


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def get_current_user_id() -> str:
    """
    Get current user ID from request context
    TODO: Implement proper authentication/authorization
    For now, accepts user_id from query param or header
    """
    # In production: Extract from JWT token or session
    return "user_default"  # Placeholder


# ═══════════════════════════════════════════════════════════════════
# ENDPOINT 1: POST /api/v1/p2p/{agreement_id}/lock-tst
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/p2p/{agreement_id}/lock-tst",
    response_model=LockTSTResponse,
    summary="Lock TST for P2P Agreement",
    description="""
    Lock TST tokens for execution of a P2P agreement.
    
    The amount locked depends on the agreement's risk tier:
    - Tier 1: 10 TST
    - Tier 2: 50 TST  
    - Tier 3+: 250 TST
    
    Locked TST is held in smart contract until agreement expires or is terminated.
    """,
    responses={
        200: {"description": "TST successfully locked"},
        400: {"description": "Invalid request (insufficient balance, invalid tier, etc.)", "model": ErrorResponse},
        401: {"description": "Unauthorized - user not authenticated", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def lock_tst_for_agreement(
    agreement_id: str = Path(..., description="P2P agreement ID"),
    request: LockTSTRequest = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Lock TST tokens for a P2P agreement.
    
    Flow:
    1. Validate user has sufficient TST balance
    2. Call P2PAgreementEscrow smart contract
    3. Store lock record in database
    4. Return lock confirmation with transaction hash
    
    Args:
        agreement_id: The P2P agreement this lock is for
        request: LockTSTRequest with amount and agreement_id
        user_id: Current user (from auth context)
    
    Returns:
        LockTSTResponse: Confirmation with lock_id, tx_hash, etc.
    """
    try:
        # Validate input
        if not request:
            raise HTTPException(status_code=400, detail="Request body required")
        
        if not agreement_id:
            raise HTTPException(status_code=400, detail="Agreement ID required")
        
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        # TODO: Get database connection from dependency injection
        db = None  # db = Depends(get_db)
        
        # Call service to lock TST
        result = await tst_service.lock_tst_for_agreement(
            user_id=user_id,
            amount=request.amount,
            agreement_id=agreement_id,
            duration_seconds=7 * 24 * 3600,  # 7 days default
            db=db
        )
        
        return LockTSTResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lock TST: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# ENDPOINT 2: POST /api/v1/strategies/{strategy_id}/upgrade-tier
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/strategies/{strategy_id}/upgrade-tier",
    response_model=UpgradeTierResponse,
    summary="Upgrade Access Tier",
    description="""
    Stake TST to upgrade access tier for entity compute quotas.
    
    Tier requirements:
    - Tier 1: 5 TST → 5 entities/day
    - Tier 2: 25 TST → 10 entities/day
    - Tier 3: 100 TST → 20 entities/day
    
    Stake duration: Fixed 30 days. TST is returned in full after expiry.
    """,
    responses={
        200: {"description": "Tier successfully upgraded"},
        400: {"description": "Invalid request (insufficient balance, invalid tier)", "model": ErrorResponse},
        401: {"description": "Unauthorized - user not authenticated", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def upgrade_access_tier(
    strategy_id: str = Path(..., description="Strategy ID (for context)"),
    request: UpgradeTierRequest = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Upgrade user's access tier by staking TST.
    
    Flow:
    1. Validate tier is 1, 2, or 3
    2. Verify user has required TST balance
    3. Call AccessTierStaking smart contract
    4. Store stake record in database (30-day duration)
    5. Return tier confirmation with benefits
    
    Args:
        strategy_id: Strategy context for this tier upgrade
        request: UpgradeTierRequest with tier level
        user_id: Current user (from auth context)
    
    Returns:
        UpgradeTierResponse: Confirmation with stake_id, tier benefits, etc.
    """
    try:
        if not request:
            raise HTTPException(status_code=400, detail="Request body required")
        
        if request.tier not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Tier must be 1, 2, or 3")
        
        # TODO: Get database connection
        db = None
        
        # Call service to upgrade tier
        result = await tst_service.upgrade_access_tier(
            user_id=user_id,
            target_tier=request.tier,
            strategy_id=strategy_id,
            db=db
        )
        
        return UpgradeTierResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade tier: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# ENDPOINT 3: POST /api/v1/entities/{entity_id}/reserve-compute
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/entities/{entity_id}/reserve-compute",
    response_model=ReserveComputeResponse,
    summary="Reserve Entity Compute Quota",
    description="""
    Reserve compute quota for an entity (Risk, Strategy, or Memory).
    
    Requires active tier. Daily quota depends on tier:
    - Tier 1: 5 entities/day
    - Tier 2: 10 entities/day
    - Tier 3: 20 entities/day
    
    Each entity type has independent daily quota.
    Quota resets daily at UTC 00:00.
    """,
    responses={
        200: {"description": "Quota successfully reserved"},
        400: {"description": "Invalid request (no active tier, quota exceeded)", "model": ErrorResponse},
        401: {"description": "Unauthorized - user not authenticated", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def reserve_entity_quota(
    entity_id: str = Path(..., description="Entity ID (risk_id, strategy_id, or memory_id)"),
    request: ReserveComputeRequest = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Reserve compute quota for an entity.
    
    Flow:
    1. Verify user has active tier
    2. Check entity type quota availability for today
    3. Call EntityComputeReserve smart contract
    4. Update quota record in database
    5. Return reservation confirmation
    
    Args:
        entity_id: The entity requesting compute
        request: ReserveComputeRequest with entity_type
        user_id: Current user (from auth context)
    
    Returns:
        ReserveComputeResponse: Confirmation with quota status
    """
    try:
        if not request:
            raise HTTPException(status_code=400, detail="Request body required")
        
        if request.entity_type not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Entity type must be 1 (Risk), 2 (Strategy), or 3 (Memory)")
        
        # TODO: Get database connection
        db = None
        
        # Call service to reserve quota
        result = await tst_service.reserve_entity_quota(
            user_id=user_id,
            entity_type=request.entity_type,
            entity_id=entity_id,
            db=db
        )
        
        return ReserveComputeResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reserve quota: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# ENDPOINT 4: GET /api/v1/tst/requirements/{action}
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/tst/requirements/{action}",
    response_model=TSTRequirementsResponse,
    summary="Get TST Requirements for Action",
    description="""
    Get TST requirements and tier options for a specific action.
    
    Supported actions:
    - lock_p2p: Lock TST for P2P agreement
    - upgrade_tier: Upgrade access tier
    - reserve_entity: Reserve entity compute quota
    """,
    responses={
        200: {"description": "Requirements retrieved successfully"},
        400: {"description": "Invalid action", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_tst_requirements(
    action: str = Path(..., description="Action name: lock_p2p, upgrade_tier, or reserve_entity")
):
    """
    Get TST requirements for a specific action.
    
    This endpoint doesn't require authentication - it provides public information
    about what's needed to perform various TST-related actions.
    
    Args:
        action: The action name to get requirements for
    
    Returns:
        TSTRequirementsResponse: Requirements with tier info and benefits
    """
    try:
        requirements = tst_service.get_tst_requirements(action)
        
        return TSTRequirementsResponse(
            action=action,
            requirements=ActionRequirement(**requirements)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get requirements: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# ENDPOINT 5: GET /api/v1/tst/access/{user_id}
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/tst/access/{user_id}",
    response_model=TSTAccessResponse,
    summary="Get User TST Access Status",
    description="""
    Get user's complete TST access status including:
    - Total balance and allocation (available, locked, staked)
    - Current active tier and expiry
    - Active locks for P2P agreements
    - Active stakes for tier access
    - Entity compute quotas status
    """,
    responses={
        200: {"description": "Access status retrieved successfully"},
        401: {"description": "Unauthorized - cannot view other user's data", "model": ErrorResponse},
        404: {"description": "User not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_tst_access_status(
    user_id: str = Path(..., description="User ID"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get user's TST access status.
    
    Security: Users can only view their own access status.
    Admins can view any user's status.
    
    Flow:
    1. Verify user is requesting own data (or is admin)
    2. Query database for balances, locks, stakes, quotas
    3. Aggregate and return comprehensive status
    
    Args:
        user_id: User ID to get access status for
        current_user_id: Current authenticated user (from auth context)
    
    Returns:
        TSTAccessResponse: Complete access status
    """
    try:
        # Authorization check
        # TODO: Implement proper auth check (allow admin override)
        if user_id != current_user_id:
            raise HTTPException(status_code=401, detail="Cannot view other user's access status")
        
        # TODO: Get database connection
        db = None
        
        # Call service to get access status
        status = await tst_service.get_user_access_status(
            user_id=user_id,
            db=db
        )
        
        return TSTAccessResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get access status: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINT
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/tst/health",
    summary="TST Service Health Check",
    description="Health check endpoint for TST service availability"
)
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Check if contracts are accessible
        # TODO: Verify contract connections
        is_healthy = True  # tst_service.w3.is_connected()
        
        if is_healthy:
            return {
                "status": "healthy",
                "service": "tst",
                "contracts_available": True
            }
        else:
            raise HTTPException(status_code=503, detail="Contract connection unavailable")
            
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
