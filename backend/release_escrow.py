import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.wallet_service import WalletService
from app.core.config import settings

async def main():
    service = WalletService()
    chain = "bsc"
    agreement_id = 2  # Hardcoded from previous audit
    
    # Identify Treasury (Payer)
    wallet_deployer = service.generate_evm_address(-1)
    addr_deployer = wallet_deployer["address"]
    
    # Identify Alice (Payee) for balance check
    wallet_alice = service.generate_evm_address(2)
    addr_alice = wallet_alice["address"]
    tst_addr = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
    
    print(f"--- PRE-RELEASE CHECK ---")
    print(f"Payer: {addr_deployer}")
    print(f"Alice: {addr_alice}")
    
    old_bal = service.get_token_balance(addr_alice, tst_addr, chain)
    print(f"Alice Balance BEFORE: {old_bal:,.2f} TST")
    
    print(f"\n🔓 Releasing Escrow Agreement #{agreement_id}...")
    
    try:
        tx_hash = await service.release_tst_escrow(
            from_index=-1, 
            agreement_id=agreement_id, 
            chain=chain
        )
        print(f"✅ RELEASE SUBMITTED!")
        print(f"📜 TX Hash: {tx_hash}")
        print(f"🔗 View on BscScan: https://bscscan.com/tx/{tx_hash}")
        
        print("\n⏳ Waiting for confirmation and balance update...")
        w3 = service.w3_bsc if settings.NEXT_PUBLIC_USE_MAINNET else service.w3_bsc_testnet
        
        for i in range(20):
            await asyncio.sleep(3)
            new_bal = service.get_token_balance(addr_alice, tst_addr, chain)
            if new_bal > old_bal:
                print(f"✅ SUCCESS! Funds Arrived.")
                print(f"Alice Balance AFTER:  {new_bal:,.2f} TST")
                break
            print(f"   ... waiting (bal={new_bal:,.2f})")
            
    except Exception as e:
        print(f"❌ Release Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
