from typing import List, Optional, Dict, Any
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
    
class CexConfigUpdate(BaseModel):
    cex_config: Dict[str, Any]

class UserResponse(UserBase):
    id: UUID
    derivation_index: int
    wallets: List[Wallet] = []
    cex_config: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True
