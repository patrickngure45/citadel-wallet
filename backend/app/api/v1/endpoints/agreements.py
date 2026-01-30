from typing import Any, List
import uuid
import uuid as uuid_pkg
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.agreement import Agreement, AgreementStatus
from app.schemas.agreement import AgreementCreate, AgreementResponse
from app.services.wallet_service import wallet_service
from app.services.access_control import access_control

router = APIRouter()

@router.post("/{user_id}/create", response_model=AgreementResponse)
async def create_p2p_agreement(
    user_id: uuid.UUID,
    data: AgreementCreate = Body(...),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Creates a new P2P Escrow Agreement.
    
    GATE: Requires 100 TST tokens.
    LOGIC: Verifies balance and freezes funds (mock).
    """
    # 1. Fetch User
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Derive Wallet Address
    user_wallet = wallet_service.generate_evm_address(user.derivation_index)
    user_address = user_wallet["address"]

    # 3. CHECK TST ACCESS (The Gate)
    REQUIRED_TST = 100
    has_access = access_control.check_access(user_address, REQUIRED_TST)

    if not has_access:
        # Get current balance just for the error message
        current = wallet_service.get_token_balance(user_address, "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71", "bsc")
        raise HTTPException(
            status_code=403, 
            detail=f"TST GATE: You hold {current} TST. Required: {REQUIRED_TST} TST. Please acquire TST to access this feature."
        )

    # 4. Create Agreement Record
    
    # Optional: Look up counterparty by email if they exist
    counterparty = None
    if data.counterparty_email:
        cp_res = await db.execute(select(User).filter(User.email == data.counterparty_email))
        counterparty = cp_res.scalars().first()

    agreement = Agreement(
        creator_id=user.id,
        counterparty_id=counterparty.id if counterparty else None,
        counterparty_email=data.counterparty_email,
        chain=data.chain,
        token_symbol=data.token_symbol,
        amount=data.amount,
        status=AgreementStatus.PENDING 
    )
    
    db.add(agreement)
    await db.commit()
    await db.refresh(agreement)
    
    return agreement

@router.get("/{user_id}/list", response_model=List[AgreementResponse])
async def list_user_agreements(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all agreements where the user is Creator or Counterparty.
    """
    result = await db.execute(
        select(Agreement).filter(
            (Agreement.creator_id == user_id) | (Agreement.counterparty_id == user_id)
        ).order_by(Agreement.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{user_id}/tier", response_model=dict)
async def get_user_access_tier(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check your TST Status Tier.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_wallet = wallet_service.generate_evm_address(user.derivation_index)
    
    tier = await access_control.get_user_tier(user_wallet["address"])
    
    return {
        "user_id": user_id,
        "address": user_wallet["address"],
        "tier": tier
    }
