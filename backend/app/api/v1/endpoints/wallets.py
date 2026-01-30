from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.models.wallet import Wallet
from app.services.wallet_service import wallet_service

router = APIRouter()

class BalanceResponse(BaseModel):
    chain: str
    address: str
    balance: float
    symbol: str

@router.get("/{user_id}/balances", response_model=List[BalanceResponse])
async def get_wallet_balances(
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Fetch current balances for all wallets belonging to a user.
    """
    # 1. Fetch user wallets
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallets = result.scalars().all()
    
    if not wallets:
        return [] # Or raise 404 if user must have wallets

    balances = []
    
    # Symbols Map
    symbols = {
        "ethereum": "ETH",
        "bsc": "BNB",
        "polygon": "MATIC"
    }

    # 2. Iterate and fetch live balances
    # In prod, do this in parallel using asyncio.gather
    for w in wallets:
        balance = await wallet_service.get_balance(w.address, w.chain)
        balances.append({
            "chain": w.chain,
            "address": w.address,
            "balance": balance,
            "symbol": symbols.get(w.chain.lower(), "ETH")
        })
        
    return balances
