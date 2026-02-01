import os
import sys
from web3 import Web3

# Config
BSC_TESTNET_RPC = "https://data-seed-prebsc-1-s1.binance.org:8545/"
TX_HASH = "0xa57842da448368242c4d4f56d553283f2c5c9a8cf7aeafce061d20eb5a946fd0"

# ABI for Event AgreementCreated
# event AgreementCreated(uint256 indexed agreementId, address indexed payer, address indexed payee, uint256 amount);
EVENT_ABI_CREATED = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "internalType": "uint256", "name": "agreementId", "type": "uint256"},
        {"indexed": True, "internalType": "address", "name": "payer", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "payee", "type": "address"},
        {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
    ],
    "name": "AgreementCreated",
    "type": "event"
}

# event FundsReleased(uint256 indexed agreementId, address indexed payee, uint256 amount);
EVENT_ABI_RELEASED = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "internalType": "uint256", "name": "agreementId", "type": "uint256"},
        {"indexed": True, "internalType": "address", "name": "payee", "type": "address"},
        {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
    ],
    "name": "FundsReleased",
    "type": "event"
}

def check_tx():
    w3 = Web3(Web3.HTTPProvider(BSC_TESTNET_RPC))
    if not w3.is_connected():
        print("Failed to connect to BSC Testnet")
        return

    print(f"Checking Transaction: {TX_HASH}")
    
    try:
        receipt = w3.eth.get_transaction_receipt(TX_HASH)
    except Exception as e:
        print(f"Error fetching receipt: {e}")
        return

    print(f"Status: {receipt['status']} (1=Success)")
    
    # Simple log decoding
    contract = w3.eth.contract(abi=[EVENT_ABI_CREATED, EVENT_ABI_RELEASED])
    
    # Process Receipt Logs
    found = False
    for log in receipt['logs']:
        try:
            # Try Created
            event = contract.events.AgreementCreated().process_log(log)
            args = event['args']
            print("\n✅ AGREEMENT CREATED FOUND!")
            print(f"Agreement ID: {args['agreementId']}")
            print(f"Amount:       {w3.from_wei(args['amount'], 'ether')} BNB")
            found = True
        except:
            pass
            
        try:
            # Try Released
            event = contract.events.FundsReleased().process_log(log)
            args = event['args']
            print("\n✅ AGREEMENT RELEASED FOUND!")
            print(f"Agreement ID: {args['agreementId']}")
            print(f"Payee:        {args['payee']}")
            print(f"Amount:       {w3.from_wei(args['amount'], 'ether')} BNB")
            found = True
        except:
            pass
            
    if not found:
        print("No relevant events found in this transaction.")

if __name__ == "__main__":
    check_tx()
