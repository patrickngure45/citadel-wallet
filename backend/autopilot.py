import asyncio
import uuid
import sys
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.entities.arena import Arena
from app.models.hearing import HearingRecordModel
# Import all models to ensure SQLA registry is populated (fixes Mapper errors)
import app.db.base 

# Add project root to path to ensure imports work if run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuration
SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001") # The "Autopilot" Identity
POLL_INTERVAL = 30 # Seconds

async def save_record(record, session: AsyncSession):
    """Persist the hearing record to the database for UI visibility."""
    try:
        db_record = HearingRecordModel(
            id=uuid.UUID(record.id),
            user_id=SYSTEM_USER_ID, 
            intent=record.intent,
            started_at=record.started_at,
            transcript=record.model_dump(mode='json'),
            final_verdict=record.final_verdict,
            final_reason=record.final_reason
        )
        session.add(db_record)
        await session.commit()
        print(f"📝 Logged to Matrix: {record.id}")
    except Exception as e:
        print(f"⚠️ DB Save Error: {e}")

async def run_autopilot():
    print("="*50)
    print("✈️  CITADEL AUTOPILOT ENGAGED")
    print("="*50)
    print(f"Identity: {SYSTEM_USER_ID}")
    print(f"Interval: {POLL_INTERVAL}s")
    print("Mode: ACTIVE HUNTING")
    
    arena = Arena()
    
    while True:
        print("\n🔎 Scanning Market Conditions...")
        
        # 1. Run the Hearing (The Brain)
        # We explicitly ask to "Analyze Market" to trigger the Alpha Hunter
        record = await arena.conduct_hearing(
            user_id=str(SYSTEM_USER_ID),
            intent="AUTOPILOT: Analyze market for high-yield arbitrage opportunities",
            execute=True 
        )
        
        # 2. Console Feedback
        print(f"Verdict: {record.final_verdict}")
        if record.strategy and record.strategy.selected_option_index != -1:
            action = record.strategy.feasible_options[record.strategy.selected_option_index].action_type
            print(f"Action: {action}")
            if record.execution and record.execution.status == "SUCCESS":
                print(f"Profit TX: {record.execution.tx_hash}")
        
        # 3. Persist to DB (The Memory)
        async with AsyncSessionLocal() as session:
            await save_record(record, session)
            
        print(f"Sleeping for {POLL_INTERVAL}s...")
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(run_autopilot())
    except KeyboardInterrupt:
        print("\n🛑 Autopilot Disengaged.")
