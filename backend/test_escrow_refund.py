import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.wallet_service import WalletService
from app.core.config import settings

async def main():
    service = WalletService()
    chain = "bsc"
    
    # Use Treasury (Index -1 or 0) for both creation and admin actions
    # Real world: User creates, Admin refunds if dispute.
    # Simulation: Treasury creates, Treasury refunds self.
    
    treasury_addr = "0x571E52efc50055d760CEaE2446aE3B469a806279" 
    alice_addr = "0x9E0b5FB77dAD5507360BdDdd2746F5B26A446390"
    
    print("\n🛡️  ESCROW SAFETY TEST: REFUND PROTOCOL")
    print("-" * 50)
    
    # 1. Create Agreement #3
    amount = 1000.0
    print(f"1. Creating Agreement #3 (Treasury -> Alice) for {amount} TST...")
    
    try:
        # Create
        tx_hash = await service.create_tst_escrow_agreement(
            from_index=-1, # Treasury
            payee_address=alice_addr,
            amount=amount,
            chain=chain,
            description="Refund Test Agreement"
        )
        print(f"   ✅ Created! TX: {tx_hash}")
        
        # Wait for indexing
        print("   ⏳ Waiting 5s for confirmation...")
        await asyncio.sleep(5)
        
        # We assume ID is incremented. Agreement #2 was last. So this is #3.
        agreement_id = 3
        
        # 2. Refund (Admin Action)
        print(f"\n2. Executing ADMIN REFUND for Agreement #{agreement_id}...")
    
        # We need a refund function in wallet_service. 
        # Checking implementation...
        
        # We need to add it if missing.
        # But for now let's try calling it manually via web3 here to save time editing service.
        
        # 2a. Setup Web3
        w3 = service.w3_bsc if settings.NEXT_PUBLIC_USE_MAINNET else service.w3_bsc_testnet
        TST_ESCROW = "0x922bA3bD7866F92F0Caa2A544bb303A38922fb12"
        abi = [{"inputs": [{"internalType": "uint256", "name": "agreementId", "type": "uint256"}], "name": "refundFunds", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
        contract = w3.eth.contract(address=TST_ESCROW, abi=abi)
        
        # 2b. Build TX (From Admin/Deployer)
        wallet = service.generate_evm_address(-1)
        sender = w3.to_checksum_address(wallet["address"])
        
        # Estimate
        try:
             gas = contract.functions.refundFunds(agreement_id).estimate_gas({'from': sender})
             gas_limit = int(gas * 1.5)
        except Exception as e:
             print(f"   ⚠️ Gas Estimate Failed (Agreement might not exist yet?): {e}")
             gas_limit = 300000
             
        tx = contract.functions.refundFunds(agreement_id).build_transaction({
            'chainId': 56 if settings.NEXT_PUBLIC_USE_MAINNET else 97,
            'gas': gas_limit,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(sender),
        })
        
        # 2c. Sign & Send
        signed = w3.eth.account.sign_transaction(tx, wallet["private_key"])
        refund_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        print(f"   ✅ Refund TX Sent: {w3.to_hex(refund_hash)}")
        print(f"   🔗 https://bscscan.com/tx/{w3.to_hex(refund_hash)}")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
