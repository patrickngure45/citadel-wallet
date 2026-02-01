import asyncio
from app.db.session import AsyncSessionLocal
from app.models.hearing import HearingRecordModel
from sqlalchemy import select, desc
from datetime import datetime, timedelta

async def check():
    async with AsyncSessionLocal() as db:
        # Mimic agent.py
        result = await db.execute(
            select(HearingRecordModel)
            .filter(HearingRecordModel.intent.like("AUTOPILOT%"))
            .order_by(desc(HearingRecordModel.started_at))
            .limit(1)
        )
        last_auto = result.scalars().first()
        
        current_utc = datetime.utcnow()
        print(f"Current UTC (Naive): {current_utc}")
        
        if last_auto:
            last_active = last_auto.started_at
            print(f"DB Raw: {last_active}")
            print(f"DB Tzinfo: {last_active.tzinfo}")
            
            # Mimic Logic
            t_check = last_active
            if t_check.tzinfo is not None:
                print("Removing tzinfo...")
                t_check = t_check.replace(tzinfo=None)
            
            print(f"Check Time: {t_check}")
            
            diff = current_utc - t_check
            print(f"Diff: {diff}")
            
            is_online = diff < timedelta(minutes=2) and diff > timedelta(seconds=-30)
            print(f"Status ONLINE? {is_online}")

if __name__ == "__main__":
    asyncio.run(check())
