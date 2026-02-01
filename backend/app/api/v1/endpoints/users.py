from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import UserCreate, UserResponse, CexConfigUpdate
from app.services.wallet_service import wallet_service

router = APIRouter()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get generic user data by ID.
    """
    try:
        import uuid
        u_uuid = uuid.UUID(user_id)
        result = await db.execute(
            select(User)
            .options(selectinload(User.wallets))
            .where(User.id == u_uuid)
        )
        user = result.scalars().first()
        if not user:
             raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid User ID")

@router.get("/{user_id}/cex-balances")
async def get_cex_balances(
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get live balances from configured CEX (Binance).
    """
    try:
        import uuid
        from app.services.cex_service import cex_service
        from app.core.config import settings
        
        u_uuid = uuid.UUID(user_id)
        result = await db.execute(
            select(User)
            .where(User.id == u_uuid)
        )
        user = result.scalars().first()
        
        if not user:
             raise HTTPException(status_code=404, detail="User not found")
        
        config = user.cex_config or {}
        binance_config = config.get("binance", {})
        
        # Priority: DB Config > Environment Variables
        api_key = binance_config.get("api_key") or settings.BINANCE_API_KEY
        api_secret = binance_config.get("api_secret") or settings.BINANCE_API_SECRET
        
        if not api_key:
            return {"status": "not_configured", "balances": []}
            
        # Fetch Real Balances
        balances = await cex_service.get_user_balance("binance", api_key, api_secret)
        
        # Format for Frontend (List)
        formatted = []
        for asset, amount in balances.items():
            formatted.append({
                "symbol": asset,
                "amount": amount,
                "value_usd": 0 # We could fetch price here if needed
            })
            
        return {"status": "connected", "balances": formatted}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/cex-config", response_model=UserResponse)
async def update_cex_config(
    user_id: str,
    config_in: CexConfigUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update CEX Configuration (API Keys).
    """
    try:
        # Cast str to UUID logic happens in DB typically, but let's be careful
        import uuid
        u_uuid = uuid.UUID(user_id)
        
        result = await db.execute(
            select(User)
            .options(selectinload(User.wallets))
            .where(User.id == u_uuid)
        )
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update JSON config
        # Merge or Replace? Let's Replace for simplicity
        user.cex_config = config_in.cex_config
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
        
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid User ID format")

@router.post("", response_model=UserResponse)
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
