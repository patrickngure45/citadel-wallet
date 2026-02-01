import asyncio
import uuid
from app.db.session import AsyncSessionLocal
from app.models.hearing import HearingRecordModel
from datetime import datetime

async def insert_dummy():
    async with AsyncSessionLocal() as db:
        new_rec = HearingRecordModel(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            intent="DEBUG_TIME_TEST",
            started_at=datetime.utcnow(),
            transcript={},
            final_verdict="ALLOWED",
            final_reason="Testing"
        )
        db.add(new_rec)
        await db.commit()
        print(f"Inserted record at {new_rec.started_at}")

if __name__ == "__main__":
    asyncio.run(insert_dummy())
