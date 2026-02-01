import asyncio
from app.db.session import AsyncSessionLocal
from app.models.hearing import HearingRecordModel
from sqlalchemy import select, desc

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(HearingRecordModel)
            .filter(HearingRecordModel.intent.ilike("%arbitrage%"))
            .order_by(desc(HearingRecordModel.started_at))
            .limit(5)
        )
        records = result.scalars().all()
        print(f"Found {len(records)} ARBITRAGE records.")
        for r in records:
            # Extract arbitrage details if available
            spread = "N/A"
            if r.transcript and 'strategy' in r.transcript:
                 opts = r.transcript['strategy'].get('feasible_options', [])
                 if opts:
                     for step in opts[0].get('steps', []):
                         if "Spread" in step:
                             spread = step
            print(f"[{r.started_at}] {r.intent} | {r.final_verdict} | {spread}")

if __name__ == "__main__":
    asyncio.run(check())
