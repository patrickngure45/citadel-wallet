from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import UserCreate, UserResponse
from app.services.wallet_service import wallet_service

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Create new user and generate custodial wallets.
    """
    # 1. Check if user exists (Get or Create pattern)
    result = await db.execute(
        select(User)
        .options(selectinload(User.wallets))
        .filter(User.email == user_in.email)
    )
    existing_user = result.scalars().first()
    if existing_user:
        return existing_user

    # 2. Get next derivation index
    # Note: In high concurrency, use a sequence or lock. 
    # For MVP: Select max + 1
    result = await db.execute(select(func.max(User.derivation_index)))
    max_index = result.scalar()
    next_index = 1 if max_index is None else max_index + 1

    # 3. Create User
    user = User(
        email=user_in.email,
        name=user_in.name,
        derivation_index=next_index,
        is_active=True
    )
    db.add(user)
    await db.flush() # Get user ID without committing
    await db.refresh(user)

    # 4. Derive Wallet (EVM)
    # For simplicity, we use the same address for all EVM chains locally, 
    # but store them as distinct entities if needed.
    # Supported Chains: Ethereum, BSC, Polygon
    evm_wallet_data = wallet_service.generate_evm_address(next_index)
    
    chains = ["ethereum", "bsc", "polygon"]
    
    for chain in chains:
        wallet = Wallet(
            user_id=user.id,
            address=evm_wallet_data["address"],
            chain=chain,
            derivation_path=evm_wallet_data["path"]
        )
        db.add(wallet)

    await db.commit()
    # No need to refresh user individually if we are going to re-select it with options
    
    # Eager load wallets for response
    # Use selectinload to fetch the relationship asynchronously in one go
    result = await db.execute(
        select(User)
        .options(selectinload(User.wallets))
        .where(User.id == user.id)
        .execution_options(populate_existing=True)
    )
    user_loaded = result.scalars().first()
    
    return user_loaded
