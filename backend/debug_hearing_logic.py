import asyncio
import sys
# Make sure app is in path
sys.path.append(".") 

from app.entities.arena import Arena
from app.core.config import settings
import app.db.base # Fix mapper errors by importing all models

async def test_hearing():
    print("--- Testing Arena Logic ---")
    arena = Arena()
    
    user_id = "f5d1f4e6-2410-458b-8cd0-a2adcc8e7494" # ngurengure10@gmail.com from debug_users.py
    intent = "Send 10 TST to Admin"
    execute = False # Start with dry run to see if it even plans correctly
    
    print(f"Intent: {intent}")
    
    try:
        record = await arena.conduct_hearing(user_id=user_id, intent=intent, execute=execute)
        
        print(f"Verdict: {record.final_verdict}")
        print(f"Reason: {record.final_reason}")
        if record.strategy and record.strategy.feasible_options:
            print("Strategy Options:")
            for opt in record.strategy.feasible_options:
                print(f" - {opt.action_type} on {opt.target_chain}")
        else:
            print("No Strategy Options")
            
        if record.execution:
            print(f"Execution Status: {record.execution.status}")
            print(f"Logs: {record.execution.logs}")
            
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_hearing())
