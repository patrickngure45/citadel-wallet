import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Details
    chain = Column(String, nullable=False)   # bsc, polygon, ethereum
    symbol = Column(String, nullable=False)  # USDT, BNB, TST
    amount = Column(Float, nullable=False)
    
    # Type: 'DEPOSIT' (Swept from user) or 'WITHDRAWAL' (Sent to user)
    type = Column(String, nullable=False) 
    
    # Blockchain Reference
    tx_hash = Column(String, unique=True, index=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="transactions")
