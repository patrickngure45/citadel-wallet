import asyncio
import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.services.wallet_service import wallet_service

async def drain_gas():
    # Target Index 7 (The active user in demo)
    INDEX = 7
    user_data = wallet_service.generate_evm_address(INDEX)
    user_addr = user_data["address"]
    user_key = user_data["private_key"]
    
    print(f"--- SABOTAGE MISSION: DRAINING GAS FROM {user_addr} ---")
    
    w3 = wallet_service.w3_bsc_testnet
    if not w3.is_connected():
        print("Failed to connect to BSC Testnet")
        return

    balance_wei = w3.eth.get_balance(user_addr)
    print(f"Current Balance: {balance_wei} wei ({w3.from_wei(balance_wei, 'ether')} BNB)")
    
    gas_price = w3.eth.gas_price
    gas_limit = 21000
    tx_cost = gas_limit * gas_price
    
    # Send almost everything to Admin, leaving 0
    amount_to_drain = balance_wei - tx_cost
    
    if amount_to_drain <= 0:
        print("✅ Wallet is already empty (or insufficient to pay gas for drain).")
        return

    print(f"Draining {amount_to_drain} wei to Admin...")
    
    tx = {
        'nonce': w3.eth.get_transaction_count(user_addr),
        'to': "0x571E52efc50055d760CEaE2446aE3B469a806279", 
        'value': amount_to_drain,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': 97
    }
    
    try:
        signed_tx = w3.eth.account.sign_transaction(tx, user_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ DRAIN SUCCESS! TX: {w3.to_hex(tx_hash)}")
        print("Waiting for confirmation...")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Confirmed. Wallet is now empty.")
    except Exception as e:
        print(f"❌ Drain Failed: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(drain_gas())
