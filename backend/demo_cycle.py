import asyncio
import sys
import os
import time

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.services.wallet_service import wallet_service
from web3 import Web3
from app.core.config import settings

# --- CONFIG ---
TARGET_INDEX = 7  # The index of the wallet to sabotage/test
TST_CONTRACT = "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5"
AMOUNT_TST_TO_SEND = 50 

# Admin (Funder)
ADMIN_KEY = settings.DEPLOYER_PRIVATE_KEY
admin_account = wallet_service.w3_bsc_testnet.eth.account.from_key(ADMIN_KEY)

async def sabotage_and_trigger():
    print("\n🎬 STARTING LIVE DEMO: 'The Self-Healing Wallet' 🎬")
    
    # 1. IDENTIFY VICTIM
    user_data = wallet_service.generate_evm_address(TARGET_INDEX)
    user_addr = user_data["address"]
    user_key = user_data["private_key"]
    w3 = wallet_service.w3_bsc_testnet
    
    print(f"🎯 Target Wallet: {user_addr}")
    
    # 2. SABOTAGE (Drain BNB)
    print("\n😈 [STEP 1] SABOTAGE: Draining Gas...")
    balance_wei = w3.eth.get_balance(user_addr)
    gas_price = w3.eth.gas_price
    cost = 21000 * gas_price
    
    if balance_wei > cost:
        drain_amount = balance_wei - cost
        tx = {
            'nonce': w3.eth.get_transaction_count(user_addr),
            'to': admin_account.address,
            'value': drain_amount,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 97
        }
        signed = w3.eth.account.sign_transaction(tx, user_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"   -> Drained {w3.from_wei(drain_amount, 'ether')} BNB. Tx: {tx_hash.hex()}")
        
        # Wait for drain to confirm
        print("   -> Waiting for block confirmation...")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print("   ✅ Wallet Empty (Stuck State Created)")
    else:
        print("   ✅ Wallet already empty.")

    # 3. TRIGGER (Send TST Tokens)
    print("\n🎁 [STEP 2] TRIGGER: Sending TST Tokens to stuck wallet...")
    contract = w3.eth.contract(address=TST_CONTRACT, abi=[
        {"constant": False,"inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],"name": "transfer","outputs": [{"name": "", "type": "bool"}],"type": "function"},
        {"constant": True,"inputs": [],"name": "decimals","outputs": [{"name": "", "type": "uint8"}],"type": "function"}
    ])
    
    decimals = contract.functions.decimals().call()
    amount_wei = AMOUNT_TST_TO_SEND * (10**decimals)
    
    admin_tx = contract.functions.transfer(user_addr, amount_wei).build_transaction({
        'from': admin_account.address,
        'nonce': w3.eth.get_transaction_count(admin_account.address),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed_admin = w3.eth.account.sign_transaction(admin_tx, ADMIN_KEY)
    tx_hash_tst = w3.eth.send_raw_transaction(signed_admin.raw_transaction)
    print(f"   -> Sent {AMOUNT_TST_TO_SEND} TST. Tx: {tx_hash_tst.hex()}")
    print("   -> Waiting for block confirmation...")
    w3.eth.wait_for_transaction_receipt(tx_hash_tst)
    print("   ✅ Tokens Dropped.")
    
    print("\n👀 [STEP 3] WATCH DASHBOARD NOW!")
    print("The Autopilot should detect the Tokens, Realize Gas is 0, Pump Gas, and Sweep.")
    print("Look for: 'Reason: Gas Refuel & Auto-Retry' in the UI.")

if __name__ == "__main__":
    asyncio.run(sabotage_and_trigger())
