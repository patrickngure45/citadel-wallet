from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class TransactionBase(BaseModel):
    chain: str
    symbol: str
    amount: float
    type: str

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: UUID
    tx_hash: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class WithdrawalRequest(BaseModel):
    chain: str
    symbol: str
    amount: float
    destination_address: str
