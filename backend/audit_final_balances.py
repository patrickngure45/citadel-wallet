import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.wallet_service import WalletService

async def main():
    service = WalletService()
    chain = "bsc"
    
    # Addresses
    treasury_addr = "0x571E52efc50055d760CEaE2446aE3B469a806279"
    alice_addr = "0x9E0b5FB77dAD5507360BdDdd2746F5B26A446390"
    tst_addr = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
    
    print(f"📊 FINAL BALANCE AUDIT")
    print("-" * 50)
    
    # 1. Treasury (Payer + Fee Collector)
    tst_treasury = service.get_token_balance(treasury_addr, tst_addr, chain)
    print(f"🏛️  Treasury (Payer):")
    print(f"   Balance: {tst_treasury:,.2f} TST")
    print(f"   Note: This account paid 5000 and earned back 15.")
    
    # 2. Alice (Payee)
    tst_alice = service.get_token_balance(alice_addr, tst_addr, chain)
    print(f"\n👤 Alice (Payee):")
    print(f"   Balance: {tst_alice:,.2f} TST")
    
    # Verification Logic
    # Alice started with 0 (assumed from previous logs). Now has 4985.
    if tst_alice == 4985.0:
        print("\n✅ AUDIT PASS: Alice received exactly 4,985.00 TST")
    else:
        print(f"\n⚠️ AUDIT WARN: Alice has {tst_alice} (Expected 4985.0)")

if __name__ == "__main__":
    asyncio.run(main())
