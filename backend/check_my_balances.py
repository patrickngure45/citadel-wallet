import asyncio
import sys
import os
from eth_account import Account

# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.wallet_service import wallet_service
from app.core.config import settings

# TST Token Addresses
TST_BSC_MAINNET = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
TST_BSC_TESTNET = "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5"

async def main():
    print("═══════════════════════════════════════════════════════════════════")
    print(" CITADEL PROTOCOL - WALLET AUDIT (REAL FUNDS CHECK)")
    print("═══════════════════════════════════════════════════════════════════")
    print(f"Environment: {'MAINNET' if settings.NEXT_PUBLIC_USE_MAINNET else 'TESTNET'}")
    
    # --- 1. DEPLOYER / ADMIN WALLET ---
    if settings.DEPLOYER_PRIVATE_KEY:
        try:
            deployer_acct = Account.from_key(settings.DEPLOYER_PRIVATE_KEY)
            deployer_addr = deployer_acct.address
            print(f"\n[DEPLOYER / ADMIN] {deployer_addr}")
            
            # Check BNB (Gas) -> Check Mainnet & Testnet
            bnb_main = await wallet_service.get_balance(deployer_addr, "bsc")
            print(f"   BNB (Mainnet): {bnb_main:.6f} BNB")
            
            # Check TST (Mainnet)
            tst_main = wallet_service.get_token_balance(deployer_addr, TST_BSC_MAINNET, "bsc")
            print(f"   TST (Mainnet): {tst_main:.2f} TST")

            # Check TST (Testnet)
            tst_test = wallet_service.get_token_balance(deployer_addr, TST_BSC_TESTNET, "bsc_testnet")
            print(f"   TST (Testnet): {tst_test:.2f} TST (BSC Testnet)")
            
        except Exception as e:
            print(f"   DEPLOYER ERR: {e}")
    else:
        print("\n[DEPLOYER] No Private Key configured.")

    # --- 2. DERIVED USER WALLETS ---
    print("\n--- DERIVED USER WALLETS (From Seed) ---")
    for i in range(5):
        wallet = wallet_service.generate_evm_address(i)
        address = wallet["address"]
        
        print(f"\n[USER ID {i}] {address}")
        
        # ETH
        try:
            eth_bal = await wallet_service.get_balance(address, "ethereum")
            if eth_bal > 0: print(f"   ETH:   {eth_bal:.6f} ETH")
        except: pass
        
        # BSC (BNB)
        try:
            bsc_bal = await wallet_service.get_balance(address, "bsc")
            if bsc_bal > 0: print(f"   BNB:   {bsc_bal:.6f} BNB")
        except: pass

        # TST (Mainnet)
        try:
            tst_bal = wallet_service.get_token_balance(address, TST_BSC_MAINNET, "bsc")
            if tst_bal > 0: print(f"   TST (Main): {tst_bal:.2f} TST")
        except: pass

        # TST (Testnet)
        try:
            tst_test_bal = wallet_service.get_token_balance(address, TST_BSC_TESTNET, "bsc_testnet")
            if tst_test_bal > 0: print(f"   TST (Test): {tst_test_bal:.2f} TST")
        except: pass
        
    print("\n═══════════════════════════════════════════════════════════════════")
    print(" AUDIT COMPLETE")
    print("═══════════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    asyncio.run(main())