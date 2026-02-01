import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.wallet_service import WalletService

async def main():
    service = WalletService()
    chain = "bsc"
    
    # Citadel Treasury / Fee Collector (Index 0 / -1 overlap logic)
    # Based on the transfer log, the fee went to 0x571E...
    treasury_addr = "0x571E52efc50055d760CEaE2446aE3B469a806279"
    tst_addr = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
    
    print(f"🏦 FEE COLLECTION WALLET AUDIT")
    print(f"Address: {treasury_addr}")
    
    # Get Balances
    tst_bal = service.get_token_balance(treasury_addr, tst_addr, chain)
    bnb_bal = await service.get_balance(treasury_addr, chain)
    
    print(f"\n📊 Current Holdings:")
    print(f"   BNB: {bnb_bal:,.6f}")
    print(f"   TST: {tst_bal:,.2f}")
    
    print(f"\n📈 Recent Revenue:")
    print(f"   +15.00 TST (Escrow Fee from Agreement #2)")

if __name__ == "__main__":
    asyncio.run(main())
