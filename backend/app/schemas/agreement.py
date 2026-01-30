from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AgreementBase(BaseModel):
    title: Optional[str] = "P2P Agreement"
    counterparty_email: str
    chain: str
    token_symbol: str
    amount: float

class AgreementCreate(AgreementBase):
    pass

class AgreementUpdate(BaseModel):
    status: Optional[str] = None
    counterparty_id: Optional[UUID] = None

class AgreementResponse(AgreementBase):
    id: UUID
    creator_id: UUID
    counterparty_id: Optional[UUID]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
