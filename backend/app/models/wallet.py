import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    address = Column(String, index=True, nullable=False)
    chain = Column(String, index=True, nullable=False) # e.g., 'ethereum', 'bsc', 'polygon'
    derivation_path = Column(String, nullable=False)   # e.g., "m/44'/60'/0'/0/1"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="wallets")
