from typing import List, Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

# Wallet Schemas
class WalletBase(BaseModel):
    chain: str
    address: str
    
class Wallet(WalletBase):
    id: UUID
    derivation_path: str

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID
    derivation_index: int
    wallets: List[Wallet] = []

    class Config:
        from_attributes = True
