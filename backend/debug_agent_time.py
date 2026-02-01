import asyncio
from app.db.session import AsyncSessionLocal
from app.models.hearing import HearingRecordModel
from sqlalchemy import select, desc
from datetime import datetime, timezone

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(HearingRecordModel)
            .filter(HearingRecordModel.intent.like("AUTOPILOT%"))
            .order_by(desc(HearingRecordModel.started_at))
            .limit(1)
        )
        last_auto = result.scalars().first()
        if last_auto:
            t = last_auto.started_at
            now = datetime.now(timezone.utc)
            
            print(f"DB Raw: {t}")
            print(f"DB Tzinfo: {t.tzinfo}")
            print(f"Now Aware: {now}")
            
            # Simulate Agent Logic
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
                
            diff = now - t
            print(f"Diff: {diff}")
            print(f"Is < 2 min? {diff.total_seconds() < 120}")

if __name__ == "__main__":
    asyncio.run(check())
