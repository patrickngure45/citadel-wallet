from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import WithdrawalRequest, TransactionResponse
from app.services.wallet_service import wallet_service
from app.core.config import settings

router = APIRouter()

@router.post("/{user_id}/withdraw", response_model=TransactionResponse)
async def request_withdrawal(
    user_id: str,
    withdrawal: WithdrawalRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Process a withdrawal request from the User's Internal Ledger Balance.
    Funds are sent from the MASTER HOT WALLET.
    """
    # 1. Verify User
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Calculate Balance (Sum of Deposits - Sum of Withdrawals)
    # in a real app, you'd maintain a cached 'balance' column on the User model.
    # For MVP, we calculate on fly.
    
    q = select(Transaction).filter(Transaction.user_id == user_id, Transaction.symbol == withdrawal.symbol)
    result = await db.execute(q)
    txs = result.scalars().all()
    
    total_deposited = sum(t.amount for t in txs if t.type == 'DEPOSIT')
    total_withdrawn = sum(t.amount for t in txs if t.type == 'WITHDRAWAL')
    available_balance = total_deposited - total_withdrawn
    
    if available_balance < withdrawal.amount:
        raise HTTPException(status_code=400, detail=f"Insufficient Funds. Available: {available_balance} {withdrawal.symbol}")

    # 3. Execute Blockchain Transfer (From Master Wallet)
    # NOTE: In production, you might queue this instead of executing synchronously.
    
    # Map symbol to contract address
    if withdrawal.chain == 'bsc' and withdrawal.symbol == 'TST':
        token_addr = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
    elif withdrawal.chain == 'bsc' and withdrawal.symbol == 'USDT':
        token_addr = "0x55d398326f99059fF775485246999027B3197955"
    elif withdrawal.chain == 'polygon' and withdrawal.symbol == 'USDT':
        token_addr = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
    else:
        raise HTTPException(status_code=400, detail="Unsupported Asset/Chain")

    try:
        # We need a method in wallet_service to send from Master Wallet
        # For now, we can reuse transfer_token logic but we need to pass the MASTER PRIVATE KEY.
        # Ideally, wallet_service has a dedicated method 'payout_user' using environment master key.
        
        # Simulating the payout function for now (Step 4 below adds it)
        tx_hash = await wallet_service.payout_from_master(
            to_address=withdrawal.destination_address,
            token_address=token_addr,
            amount=withdrawal.amount,
            chain=withdrawal.chain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4. Record Debit
    new_tx = Transaction(
        user_id=user_id,
        chain=withdrawal.chain,
        symbol=withdrawal.symbol,
        amount=withdrawal.amount,
        type='WITHDRAWAL',
        tx_hash=tx_hash
    )
    db.add(new_tx)
    await db.commit()
    await db.refresh(new_tx)
    
    return new_tx

@router.get("/{user_id}/history", response_model=List[TransactionResponse])
async def get_history(
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all deposits and withdrawals.
    """
    result = await db.execute(select(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.created_at.desc()))
    return result.scalars().all()
