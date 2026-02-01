import asyncio
import sys
import os
import requests
import uuid
from sqlalchemy import select

# Ensure we can import app modules if needed, but we'll use API mainly
sys.path.append(os.getcwd())

API_URL = "http://localhost:8000/api/v1/hearing/gate"

from app.db.session import AsyncSessionLocal
from app.models.user import User

# Fixes for SQLAlchemy relationship registry issues
# We must import ALL models that User relates to
try:
    from app.models.wallet import Wallet
    from app.models.agreement import Agreement
    from app.models.transaction import Transaction
    from app.models.hearing import HearingRecordModel
except ImportError:
    pass

async def execute_risk_simulation():
    print("\n🛡️ STARTING DEFENSE SIMULATION: 'The Citadel Moat' 🛡️")
    
    # 1. Get User
    # Note: User model doesn't store wallet_address, it's derived.
    # But for this test, we know the email: 'azurefashion254@gmail.com' or 'test@citadel.com'
    # Actually, let's just use the known User ID if we can find it by email.
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).filter(User.email == "test@citadel.com"))
        user = result.scalars().first()
        if not user:
             # Fallback to the other email seen in admin_faucet
             result = await db.execute(select(User).filter(User.email == "azurefashion254@gmail.com"))
             user = result.scalars().first()
        
        if not user:
            print("Test user not found by email. Please update script with valid email.")
            return
        user_id = str(user.id)
    
    print(f"Authenticated User: {user_id} (from DB)")

    # TEST A: THE "FAT FINGER" (Send 1 Billion ETH)
    print("\n[TEST 1] 🚨 SIMULATION: Accidental 'Fat Finger' Transfer")
    payload_1 = {
        "user_id": user_id,
        "intent": "Send 2000000 ETH to 0x571E52efc50055d760CEaE2446aE3B469a806279",
        "execute": True
    }
    try:
        res = requests.post(API_URL, json=payload_1)
        data = res.json()
        print(f"   Intent: {data['intent']}")
        print(f"   Verdict: {data['final_verdict']}")
        print(f"   Reason: {data['final_reason']}")
        if data['final_verdict'] == "BLOCKED":
             print("   ✅ SUCCESS: Citadel Blocked the anomaly.")
        else:
             print("   ❌ FAILURE: Transaction passed (Panic!)")
    except Exception as e:
        print(f"   Error: {e}")

    # TEST B: THE "HONEYPOT" (Send High Value to Unknown Address)
    # TST Limit is 1000. We send 2000 to a random address.
    print("\n[TEST 2] 🕵️ SIMULATION: High-Value Transfer to Untrusted Address")
    unknown_addr = "0x9999999999999999999999999999999999999999"
    payload_2 = {
        "user_id": user_id,
        "intent": f"Send 2000 TST to {unknown_addr}",
        "execute": True
    }
    try:
        res = requests.post(API_URL, json=payload_2)
        data = res.json()
        print(f"   Intent: {data['intent']}")
        print(f"   Verdict: {data['final_verdict']}")
        print(f"   Reason: {data['final_reason']}")
         
        # We expect a Block or Warning. 
        # Risk Entity says: if perceived_amount > threshold (100) -> VETO.
        # 2000 > 100. Should VETO.
        
        if data['final_verdict'] == "BLOCKED":
             print("   ✅ SUCCESS: Citadel VETOED sending to stranger.")
        else:
             print("   ❌ FAILURE: Transaction passed.")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n✨ SIMULATION COMPLETE. CHECK DASHBOARD FOR RED ALERTS. ✨")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(execute_risk_simulation())
