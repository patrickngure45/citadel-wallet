import asyncio
from app.services.access_control import access_control

USER_ADDR = "0x578FC7311a846997dc99bF2d4C651418DcFe309A" # The address from your logs

async def test_gate():
    print("="*60)
    print("PHASE 0: TESTING UTILITY GATE")
    print("="*60)
    print(f"User: {USER_ADDR}")
    print("-" * 60)

    # 1. Test Tier
    print("1. Checking Status Tier...")
    tier = await access_control.get_user_tier(USER_ADDR)
    print(f"   [RESULT] Tier: {tier}")
    
    # 2. Test Gate (Agreement Creation)
    print("\n2. Attempting to Create P2P Agreement (Req: 100 TST)...")
    has_access = access_control.check_access(USER_ADDR, 100)
    
    if has_access:
        print("   [SUCCESS] Access Granted. User has sufficient TST.")
    else:
        print("   [DENIED] Access Blocked. User needs > 100 TST.")
        
    # 3. Test High Value
    print("\n3. Attempting Institutional Action (Req: 10,000 TST)...")
    if access_control.check_access(USER_ADDR, 10000):
        print("   [SUCCESS] Access Granted.")
    else:
        print("   [DENIED] Access Blocked.")

if __name__ == "__main__":
    asyncio.run(test_gate())
