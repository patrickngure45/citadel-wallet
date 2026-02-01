
import asyncio
import time
import sys
from web3 import Web3
from app.core.config import settings

# CONFIG
RPC_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/"
CHAIN_ID = 97
TST_ADDRESS = "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5"

RECIPIENTS = [
    {"name": "User 0 (Standalone)", "addr": "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"},
    {"name": "User 1 (Ngure)", "addr": "0x578FC7311a846997dc99bF2d4C651418DcFe309A"}
]

# SEND AMOUNTS
SEND_BNB = 0.03
SEND_TST = 1000

async def fund_users():
    print(f"Connecting to BSC Testnet...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Failed to connect.")
        return

    admin_key = settings.DEPLOYER_PRIVATE_KEY
    admin_acct = w3.eth.account.from_key(admin_key)
    admin_addr = admin_acct.address
    print(f"Admin: {admin_addr}")
    
    admin_bal = w3.eth.get_balance(admin_addr)
    print(f"Admin Balance: {w3.from_wei(admin_bal, 'ether')} BNB")

    nonce = w3.eth.get_transaction_count(admin_addr)

    for rec in RECIPIENTS:
        target = rec['addr']
        print(f"--- Funding {rec['name']} ---")
        
        # 1. SEND BNB
        print(f"Sending {SEND_BNB} BNB to {target}...")
        tx_params = {
            'nonce': nonce,
            'to': target,
            'value': w3.to_wei(SEND_BNB, 'ether'),
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
            'chainId': CHAIN_ID
        }
        signed_tx = w3.eth.account.sign_transaction(tx_params, admin_key)
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"BNB Sent! Hash: {w3.to_hex(tx_hash)}")
            nonce += 1 # Increment nonce locally
        except Exception as e:
            print(f"Failed to send BNB: {e}")
            
        time.sleep(2)

        # 2. SEND TST if needed 
        print(f"Checking TST Balance for {target}...")
        try:
             # Minimal ABI for transfer
             tst_contract = w3.eth.contract(address=TST_ADDRESS, abi=[
                 {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
                 {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
             ])
             
             # Check current balance
             current_bal = tst_contract.functions.balanceOf(target).call()
             if current_bal > 0:
                 print(f"Skipping TST: User already has {w3.from_wei(current_bal, 'ether')} TST")
             else:
                 amount_wei = w3.to_wei(SEND_TST, 'ether')
                 print(f"Sending {SEND_TST} TST to {target}...")
                 tx_data = tst_contract.functions.transfer(target, amount_wei).build_transaction({
                     'nonce': nonce,
                     'gas': 100000,
                     'gasPrice': w3.eth.gas_price,
                     'chainId': CHAIN_ID
                 })
                 signed_tst = w3.eth.account.sign_transaction(tx_data, admin_key)
                 tst_hash = w3.eth.send_raw_transaction(signed_tst.raw_transaction)
                 print(f"TST Sent! Hash: {w3.to_hex(tst_hash)}")
                 nonce += 1
                 time.sleep(2)
        except Exception as e:
            print(f"Failed to send TST: {e}")
    
    print("Funding Complete.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fund_users())
