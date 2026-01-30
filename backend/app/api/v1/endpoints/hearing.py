from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.entities.arena import Arena
from app.schemas.hearing import HearingRecord
from app.models.hearing import HearingRecordModel
import uuid

router = APIRouter()
arena = Arena()

class HearingRequest(BaseModel):
    user_id: str
    intent: str
    execute: bool = False

@router.post("/gate", response_model=HearingRecord)
async def run_hearing(request: HearingRequest, db: AsyncSession = Depends(get_db)):
    """
    Submits an intent to the Entity Control Plane.
    Returns the full HearingRecord with the verdict.
    Persists the record to Postgres.
    """
    try:
        # 1. Run the Entity Loop (CPU bound, synchronous logic)
        record = arena.conduct_hearing(
            user_id=request.user_id,
            intent=request.intent,
            execute=request.execute
        )
        
        # 2. Persist to DB
        # Note: In a real app, ensure user_id is a valid UUID before casting
        try:
            u_id = uuid.UUID(request.user_id)
        except ValueError:
             # Fallback for dev if user uses non-uuid strings
            u_id = uuid.uuid4() 

        db_record = HearingRecordModel(
            id=uuid.UUID(record.id),
            user_id=u_id, 
            intent=record.intent,
            started_at=record.started_at,
            transcript=record.model_dump(), # Pydantic v2 uses model_dump()
            final_verdict=record.final_verdict,
            final_reason=record.final_reason
        )
        
        db.add(db_record)
        await db.commit()
        
        return record
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
