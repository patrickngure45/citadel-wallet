import asyncio
import os
import sys

# Add backend to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.wallet_service import WalletService
from app.core.config import settings

async def main():
    service = WalletService()
    
    chain = "bsc"
    if settings.NEXT_PUBLIC_USE_MAINNET:
        print("🌍 Using BSC MAINNET")
    else:
        print("🧪 Using BSC TESTNET")

    # TST Contract
    TST_ADDRESS = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"

    # 1. Investigate Treasury Candidates
    print("\n--- TREASURY DEBUG ---")
    
    # Candidate A: Index 0 (Mnemonic)
    wallet_0 = service.generate_evm_address(0)
    addr_0 = wallet_0["address"]
    bnb_0 = await service.get_balance(addr_0, chain)
    tst_0 = service.get_token_balance(addr_0, TST_ADDRESS, chain)
    print(f"Index 0: {addr_0} | BNB: {bnb_0:.6f} | TST: {tst_0:,.2f}")
    
    # Candidate B: Index -1 (Deployer Key)
    wallet_deployer = service.generate_evm_address(-1)
    addr_deployer = wallet_deployer["address"]
    bnb_deployer = await service.get_balance(addr_deployer, chain)
    tst_deployer = service.get_token_balance(addr_deployer, TST_ADDRESS, chain)
    print(f"Index -1: {addr_deployer} | BNB: {bnb_deployer:.6f} | TST: {tst_deployer:,.2f}")
    
    treasury_index = 0
    # Determine Source
    if tst_0 > 5000 and bnb_0 > 0.001:
        treasury_index = 0
        print("✅ Selected Index 0 as Treasury")
    elif tst_deployer > 5000 and bnb_deployer > 0.001:
        treasury_index = -1
        print("✅ Selected Index -1 as Treasury")
    else:
        print("❌ CRITICAL: No Treasury account found with sufficient TST AND BNB.")
        print("   Index 0 has TST?" + str(tst_0 > 0) + " BNB?" + str(bnb_0 > 0))
        print("   Index -1 has TST?" + str(tst_deployer > 0) + " BNB?" + str(bnb_deployer > 0))
        # return # Commented out to allow partial execution if verifying balances 

    # 2. Setup Identities
    # User (Index 1)
    user_wallet = service.generate_evm_address(1)
    user_addr = user_wallet["address"]
    
    # Alice (Index 2)
    alice_wallet = service.generate_evm_address(2)
    alice_addr = alice_wallet["address"]
    
    print(f"\nUser (Index 1): {user_addr}")
    print(f"Alice (Index 2): {alice_addr}")

    required_amount = 5000.0
    
    # 3. Create Escrow Agreement from Treasury
    # We use Treasury directly to avoid "Funding Revert" issues with User wallet
    # Treasury has plenty of TST and BNB
    
    sender_index = treasury_index
    sender_addr = addr_0 if treasury_index == 0 else addr_deployer
    
    print(f"\n🔒 Creating Escrow Agreement: Treasury ({sender_addr}) -> Alice")
    print(f"   Amount: {required_amount} TST")
    description = "Consulting Services - Phase 1"
    
    try:
        tx_hash = await service.create_tst_escrow_agreement(
            from_index=sender_index,
            payee_address=alice_addr,
            amount=required_amount,
            chain=chain,
            description=description
        )
        print(f"✅ ESCROW CREATION SUCCESSFUL!")
        print(f"📜 TX Hash: {tx_hash}")
        print(f"🔗 View on BscScan: https://bscscan.com/tx/{tx_hash}")
        
    except Exception as e:
        print(f"❌ Escrow Creation Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
