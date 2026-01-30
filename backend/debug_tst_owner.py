from web3 import Web3
from app.core.config import settings
import json

# CONFIG
TST_ADDRESS = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
DEPLOYER_KEY = settings.DEPLOYER_PRIVATE_KEY

# SETUP
w3 = Web3(Web3.HTTPProvider(settings.BSC_RPC_URL))
account = w3.eth.account.from_key(DEPLOYER_KEY)
my_address = account.address

# COMMON OWNER ABIS
OWNER_ABI = [
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "isExcludedFromFee",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "excludeFromFee",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bool", "name": "_enabled", "type": "bool"}],
        "name": "setSwapAndLiquifyEnabled",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def check_ownership():
    print("="*60)
    print("TST PROPRIETOR DIAGNOSTIC")
    print("="*60)
    print(f"Me: {my_address}")
    
    if not w3.is_connected():
        print("Error: No connection.")
        return

    contract = w3.eth.contract(address=w3.to_checksum_address(TST_ADDRESS), abi=OWNER_ABI)
    
    # 1. Check Owner
    try:
        current_owner = contract.functions.owner().call()
        print(f"Contract Owner: {current_owner}")
        
        if current_owner == my_address:
            print("   [SUCCESS] You are the OWNER.")
            try_exclude_variants(contract)
        else:
            print("   [WARNING] You are NOT the owner.")
            
    except Exception as e:
        print(f"   [!] Could not read owner(): {e}")

def try_exclude_variants(contract):
    print("\n>>> ATTEMPTING 'setIsExcludedFromFee' (Common Variant)...")
    try:
        # Common Variant 1: setIsExcludedFromFee(address, bool)
        # We need to manually construct this because ABI above didn't have it
        func_sig = w3.keccak(text="setIsExcludedFromFee(address,bool)")[0:4]
        
        # Encode args
        from eth_abi import encode
        enc_args = encode(['address', 'bool'], [my_address, True])
        
        data = func_sig + enc_args
        
        nonce = w3.eth.get_transaction_count(my_address)
        
        tx = {
            'to': w3.to_checksum_address(TST_ADDRESS),
            'value': 0,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
            'chainId': 56,
            'data': data
        }
        
        signed = w3.eth.account.sign_transaction(tx, DEPLOYER_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"Transaction Sent: {w3.to_hex(tx_hash)}")
        print("Waiting...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            print("   [SUCCESS] Excluded via setIsExcludedFromFee!")
            return
        else:
            print("   [FAILED] Reverted.")
            
    except Exception as e:
        print(f"Error: {e}")

    print("\n>>> ATTEMPTING 'excludeFromFee' (Standard Variant)...")
    try:
        contract.functions.excludeFromFee(my_address).estimate_gas({'from': my_address})
        # If estimate works, send it
        nonce = w3.eth.get_transaction_count(my_address)
        tx = contract.functions.excludeFromFee(my_address).build_transaction({
             'chainId': 56, 'gas': 100000, 'gasPrice': w3.eth.gas_price, 'nonce': nonce
        })
        signed = w3.eth.account.sign_transaction(tx, DEPLOYER_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"Transaction Sent: {w3.to_hex(tx_hash)}")
        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e2:
         print(f"   [FAILED] excludeFromFee failed: {e2}")
if __name__ == "__main__":
    check_ownership()
