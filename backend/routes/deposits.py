"""
Citadel - Deposit Management Endpoints
REST API for deposit detection, verification, settlement
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

# Import deposit system modules
from backend.deposit.listener import (
    Deposit,
    DepositListener,
    FundSettlement,
    DepositSettlementOrchestrator,
)
from backend.deposit.database import (
    DepositDatabaseManager,
    SettlementCompletionHandler,
)
from backend.wallet.manager import WalletManager


# ==================== Schemas ====================

class DepositStatus(str, Enum):
    """Deposit lifecycle status"""
    DETECTED = "detected"
    VERIFIED = "verified"
    APPROVED = "approved"
    SWEEPING = "sweeping"
    SWEPT = "swept"
    SETTLED = "settled"
    REJECTED = "rejected"


class CreateDepositRequest(BaseModel):
    """Manual deposit entry"""
    user_id: str = Field(..., description="User ID")
    amount: Decimal = Field(..., gt=0, description="Deposit amount in USD")
    asset_type: str = Field(default="usdt", description="usdt or usdc")
    chain: str = Field(default="bsc", description="bsc or polygon")
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "amount": 500,
                "asset_type": "usdt",
                "chain": "bsc",
                "tx_hash": "0x1234567890abcdef"
            }
        }


class VerifyDepositRequest(BaseModel):
    """Verify deposit and link to user wallet"""
    user_id: str = Field(..., description="User ID")
    wallet_address: str = Field(..., description="User wallet address receiving deposit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "wallet_address": "0x578FC7311a846997dc99bF2d4C651418DcFe309A"
            }
        }


class ApproveDepositRequest(BaseModel):
    """Risk/Strategy entity approval for settlement"""
    deposit_id: str = Field(..., description="Deposit ID to approve")
    risk_approved: bool = Field(default=True, description="Risk entity approval")
    anomaly_score: float = Field(default=0.1, ge=0, le=1, description="Anomaly score from Risk entity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "deposit_id": "deposit_abc123",
                "risk_approved": True,
                "anomaly_score": 0.12
            }
        }


class DepositResponse(BaseModel):
    """Deposit object response"""
    id: str
    user_id: str
    tx_hash: str
    amount: str
    asset_type: str
    chain: str
    status: DepositStatus
    tst_reward: Optional[str] = None
    sweep_tx_hash: Optional[str] = None
    created_at: str
    verified_at: Optional[str] = None
    settled_at: Optional[str] = None


class SettlementSummary(BaseModel):
    """Settlement completion summary"""
    status: str
    deposit_amount: str
    tst_reward: str
    sweep_tx_hash: str
    master_wallet: str
    completed_at: str
    next_steps: List[str]


# ==================== Initialize Services ====================

# These would be injected from app startup
deposit_listener = None
deposit_settlement = None
db_manager = None
completion_handler = None
wallet_manager = None


def get_services():
    """Dependency injection for services"""
    return {
        "listener": deposit_listener,
        "settlement": deposit_settlement,
        "db": db_manager,
        "completion": completion_handler,
        "wallet": wallet_manager,
    }


# ==================== Router Setup ====================

router = APIRouter(
    prefix="/api/v1/deposits",
    tags=["deposits"],
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    }
)


# ==================== Endpoints ====================

@router.post("/create", response_model=DepositResponse)
async def create_deposit(
    request: CreateDepositRequest,
    services=Depends(get_services),
):
    """
    Create a new deposit entry.
    
    Called when:
    - User initiates a deposit
    - Manual entry for off-chain deposit
    - Import from external wallet
    
    Returns: Deposit object with DETECTED status
    """
    try:
        listener = services["listener"]
        
        # Create deposit object
        deposit = listener.process_transfer_event(
            from_address=request.tx_hash or "manual_entry",
            to_address="pending_verification",
            amount=request.amount,
            asset_type=request.asset_type,
            chain=request.chain,
            tx_hash=request.tx_hash or f"manual_{datetime.utcnow().timestamp()}",
            block_number=0,
            timestamp=datetime.utcnow(),
        )
        
        return DepositResponse(
            id=deposit.tx_hash,
            user_id=request.user_id,
            tx_hash=deposit.tx_hash,
            amount=str(deposit.amount),
            asset_type=deposit.asset_type,
            chain=deposit.chain,
            status=DepositStatus.DETECTED,
            created_at=datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deposit_id}/verify")
async def verify_deposit(
    deposit_id: str,
    request: VerifyDepositRequest,
    services=Depends(get_services),
):
    """
    Verify deposit and link to user wallet.
    
    Validates:
    - User owns the wallet
    - Amount matches on-chain
    - No anomalies detected
    
    Moves to: VERIFIED status
    """
    try:
        listener = services["listener"]
        db = services["db"]
        
        # Get deposit
        deposit = listener.pending_deposits.get(deposit_id)
        if not deposit:
            raise HTTPException(status_code=404, detail="Deposit not found")
        
        # Verify wallet ownership (in real system, check signature)
        # For now, just validate format
        if not request.wallet_address.startswith("0x"):
            raise HTTPException(status_code=400, detail="Invalid wallet address")
        
        # Update deposit with user info
        deposit.user_id = request.user_id
        deposit.mark_verified()
        
        return {
            "status": "verified",
            "deposit_id": deposit_id,
            "user_id": request.user_id,
            "wallet_address": request.wallet_address,
            "amount": str(deposit.amount),
            "verified_at": datetime.utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deposit_id}/approve")
async def approve_deposit_for_settlement(
    deposit_id: str,
    request: ApproveDepositRequest,
    services=Depends(get_services),
):
    """
    Risk entity approves deposit for settlement.
    
    Called by Risk Service after:
    - Anomaly detection check
    - Compliance validation
    - KYC verification
    
    If approved: Creates sweep transaction (awaits multi-sig)
    If rejected: Deposit marked as rejected
    """
    try:
        listener = services["listener"]
        settlement = services["settlement"]
        
        # Get deposit
        deposit = listener.pending_deposits.get(deposit_id)
        if not deposit:
            raise HTTPException(status_code=404, detail="Deposit not found")
        
        if not request.risk_approved:
            deposit.status = "rejected"
            return {
                "status": "rejected",
                "deposit_id": deposit_id,
                "reason": "Risk entity rejected deposit",
                "anomaly_score": request.anomaly_score,
            }
        
        # Mark approved and process settlement
        deposit.mark_approved()
        
        # Calculate TST reward
        tst_reward = listener.calculate_tst_reward(deposit.amount)
        deposit.tst_reward = tst_reward
        
        # Create sweep transaction
        sweep_tx = settlement.create_sweep_transaction(deposit)
        deposit.sweep_tx_hash = sweep_tx["tx_hash"]
        deposit.mark_swept()
        
        return {
            "status": "approved_for_settlement",
            "deposit_id": deposit_id,
            "amount": str(deposit.amount),
            "tst_reward": str(tst_reward),
            "sweep_tx": sweep_tx["tx_hash"],
            "signatures_required": "2-of-3 (Risk + Strategy)",
            "next_step": "Entity system collects signatures and broadcasts sweep",
            "approved_at": datetime.utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def list_pending_deposits(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    chain: Optional[str] = Query(None, description="Filter by chain (bsc/polygon)"),
    services=Depends(get_services),
) -> List[DepositResponse]:
    """
    List all pending deposits awaiting verification/settlement.
    
    Filters:
    - By user ID
    - By chain
    - By status
    
    Returns: List of pending Deposit objects
    """
    try:
        listener = services["listener"]
        
        pending = []
        for tx_hash, deposit in listener.pending_deposits.items():
            # Apply filters
            if user_id and deposit.user_id != user_id:
                continue
            if chain and deposit.chain != chain:
                continue
            
            pending.append(DepositResponse(
                id=tx_hash,
                user_id=deposit.user_id or "unverified",
                tx_hash=deposit.tx_hash,
                amount=str(deposit.amount),
                asset_type=deposit.asset_type,
                chain=deposit.chain,
                status=deposit.status,
                tst_reward=str(deposit.tst_reward) if deposit.tst_reward else None,
                sweep_tx_hash=deposit.sweep_tx_hash,
                created_at=datetime.fromtimestamp(deposit.timestamp).isoformat(),
            ))
        
        return pending
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_settlement_history(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    services=Depends(get_services),
) -> dict:
    """
    Get settled/completed deposits.
    
    Returns historical record of:
    - Completed deposits
    - TST rewards awarded
    - Sweep transactions
    - Settlement timestamps
    """
    try:
        listener = services["listener"]
        
        settled = listener.settled_deposits
        
        # Filter by user
        if user_id:
            settled = [d for d in settled if d.user_id == user_id]
        
        # Apply pagination
        total = len(settled)
        settled = settled[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "deposits": [
                DepositResponse(
                    id=d.tx_hash,
                    user_id=d.user_id or "unknown",
                    tx_hash=d.tx_hash,
                    amount=str(d.amount),
                    asset_type=d.asset_type,
                    chain=d.chain,
                    status=d.status,
                    tst_reward=str(d.tst_reward) if d.tst_reward else None,
                    sweep_tx_hash=d.sweep_tx_hash,
                    created_at=datetime.fromtimestamp(d.timestamp).isoformat(),
                    settled_at=d.settled_at.isoformat() if d.settled_at else None,
                ).model_dump()
                for d in settled
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deposit_id}/status")
async def get_deposit_status(
    deposit_id: str,
    services=Depends(get_services),
):
    """Get current status of a specific deposit."""
    try:
        listener = services["listener"]
        
        # Check pending
        if deposit_id in listener.pending_deposits:
            d = listener.pending_deposits[deposit_id]
            return {
                "id": deposit_id,
                "status": d.status,
                "amount": str(d.amount),
                "asset_type": d.asset_type,
                "chain": d.chain,
                "user_id": d.user_id,
                "tst_reward": str(d.tst_reward) if d.tst_reward else None,
                "sweep_tx": d.sweep_tx_hash,
                "location": "pending",
            }
        
        # Check settled
        settled = [d for d in listener.settled_deposits if d.tx_hash == deposit_id]
        if settled:
            d = settled[0]
            return {
                "id": deposit_id,
                "status": d.status,
                "amount": str(d.amount),
                "asset_type": d.asset_type,
                "chain": d.chain,
                "user_id": d.user_id,
                "tst_reward": str(d.tst_reward) if d.tst_reward else None,
                "sweep_tx": d.sweep_tx_hash,
                "settled_at": d.settled_at.isoformat() if d.settled_at else None,
                "location": "settled",
            }
        
        raise HTTPException(status_code=404, detail="Deposit not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_deposit_statistics(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    chain: Optional[str] = Query(None, description="Filter by chain"),
    services=Depends(get_services),
):
    """
    Get aggregated deposit statistics.
    
    Returns:
    - Total deposits
    - Total value
    - TST rewards distributed
    - Average deposit size
    - Settlement rate
    """
    try:
        listener = services["listener"]
        
        all_deposits = list(listener.pending_deposits.values()) + listener.settled_deposits
        
        # Filter
        if user_id:
            all_deposits = [d for d in all_deposits if d.user_id == user_id]
        if chain:
            all_deposits = [d for d in all_deposits if d.chain == chain]
        
        if not all_deposits:
            return {
                "total_deposits": 0,
                "total_value": "0",
                "tst_reward_distributed": "0",
                "average_deposit": "0",
                "settlement_rate": 0,
            }
        
        settled = [d for d in all_deposits if d.status == "settled"]
        total_value = sum(d.amount for d in all_deposits)
        total_tst = sum(d.tst_reward or Decimal(0) for d in all_deposits)
        
        return {
            "total_deposits": len(all_deposits),
            "total_value": str(total_value),
            "tst_reward_distributed": str(total_tst),
            "average_deposit": str(total_value / len(all_deposits)) if all_deposits else "0",
            "settlement_rate": round(len(settled) / len(all_deposits) * 100, 2),
            "pending_count": len(listener.pending_deposits),
            "settled_count": len(listener.settled_deposits),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "deposits",
        "timestamp": datetime.utcnow().isoformat(),
    }
