from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.db.session import get_db
from app.models.hearing import HearingRecordModel
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
async def get_agent_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns the health status and recent activity of the Agent (Autopilot).
    Checks DB time to ensure consistency.
    """
    # 1. Fetch last Autopilot action
    result = await db.execute(
        select(HearingRecordModel)
        .filter(HearingRecordModel.intent.like("AUTOPILOT%"))
        .order_by(desc(HearingRecordModel.started_at))
        .limit(1)
    )
    last_auto = result.scalars().first()
    
    # Get DB Time (Source of Truth)
    time_res = await db.execute(select(func.now()))
    db_now = time_res.scalar()
    
    # 2. Determine Status
    status = "OFFLINE"
    last_active = None
    
    if last_auto and db_now:
        last_active = last_auto.started_at
        
        # Ensure consistency by using db_now
        # Postgres returns aware datetime usually
        if last_active.tzinfo is None and db_now.tzinfo is not None:
             last_active = last_active.replace(tzinfo=db_now.tzinfo)
        
        diff = db_now - last_active
        
        # 2 minutes threshold
        if diff < timedelta(minutes=2):
            status = "ONLINE"
        else:
             print(f"[AGENT] Offline. DB Now: {db_now}, Last: {last_active}, Diff: {diff}")
        
        # Handle Timezone offset mismatch
        check_time = last_active
        if check_time.tzinfo is not None:
             check_time = check_time.replace(tzinfo=None) # Make naive UTC to compare with utcnow
             
        # Replaced by Logic Above

            
    # 3. Fetch recent general actions (Top 5), excluding all Autopilot noise to show User Activity
    recent_res = await db.execute(
        select(HearingRecordModel)
        .filter(HearingRecordModel.intent.notlike("AUTOPILOT%"))
        .order_by(desc(HearingRecordModel.started_at))
        .limit(5)
    )
    recent_records = recent_res.scalars().all()
    
    actions = []
    for r in recent_records:
        actions.append({
            "id": str(r.id),
            "intent": r.intent,
            "verdict": r.final_verdict,
            "reason": r.final_reason,
            "transcript": r.transcript,
            "time": r.started_at
        })

    return {
        "status": status,
        "last_active": last_active,
        "recent_actions": actions
    }
