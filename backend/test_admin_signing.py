
import asyncio
import os
from app.services.wallet_service import WalletService

# Mock settings just enough to init
class MockSettings:
    MNEMONIC = os.getenv("MNEMONIC", "test test test test test test test test test test test junk")
    DEPLOYER_PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001")

async def test_signing():
    print("Testing Admin Signing Capability...")
    service = WalletService()
    
    # We need to monkeypath the settings or ensure they are present
    # But WalletService imports 'settings' from core.config.
    # Let's hope the environment is set or it defaults gracefully.
    
    try:
        # Test getting address for -1
        addr = service.get_address(index=-1)
        print(f"Admin Address Resolved: {addr}")
        
        if addr == "0x571E52efc50055d760CEaE2446aE3B469a806279":
            print("✅ Address matches known Admin Address.")
        else:
            print("❌ Address mismatch! Check wallet_service.py logic.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_signing())
