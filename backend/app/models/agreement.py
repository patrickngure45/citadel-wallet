import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class AgreementStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"

class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Creator of the agreement
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Counterparty (Optional initially, can be invited by email)
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    counterparty_email = Column(String, nullable=True)
    
    # Terms
    chain = Column(String, nullable=False)   # e.g. "bsc"
    token_symbol = Column(String, nullable=False) # e.g. "USDC"
    amount = Column(Float, nullable=False)
    
    status = Column(String, default=AgreementStatus.PENDING, nullable=False)
    
    # Blockchain Data (If on-chain escrow is used later)
    contract_address = Column(String, nullable=True)
    tx_hash = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], backref="created_agreements")
    counterparty = relationship("User", foreign_keys=[counterparty_id], backref="participating_agreements")
