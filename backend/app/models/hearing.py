import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base

class HearingRecordModel(Base):
    __tablename__ = "hearing_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Metadata
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    intent = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # The Full Transcript (Perception, Risk, Strategy, etc.)
    # We store this as JSONB because the structure is complex and deeply nested
    transcript = Column(JSONB, nullable=False)
    
    # Queryable Outcome
    final_verdict = Column(String, index=True, nullable=False) # ALLOWED, BLOCKED, ERROR
    final_reason = Column(String, nullable=True)

    def to_schema(self):
        """Helper to convert DB model back to Pydantic schema"""
        from app.schemas.hearing import HearingRecord
        data = self.transcript
        return HearingRecord(**data)
