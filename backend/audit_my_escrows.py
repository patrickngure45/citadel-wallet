import os
import sys
from web3 import Web3
from eth_account import Account

# Add app to path to potentially use config, but we'll try standalone first for speed
sys.path.append(os.getcwd())

# Config
BSC_TESTNET_RPC = "https://data-seed-prebsc-1-s1.binance.org:8545/"
ESCROW_ADDRESS = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"

# ABI for Event
# event AgreementCreated(uint256 indexed agreementId, address indexed payer, address indexed payee, uint256 amount);
ABI = [
    {
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
]

def check_escrows():
    w3 = Web3(Web3.HTTPProvider(BSC_TESTNET_RPC))
    if not w3.is_connected():
        print("Failed to connect to BSC Testnet")
        return

    contract = w3.eth.contract(address=ESCROW_ADDRESS, abi=ABI)
    
    print(f"Scanning Contract: {ESCROW_ADDRESS}")
    
    # Standard RPC providers on BSC Testnet are often very restrictive (e.g. 5000 block limit, or rate limited).
    # Since filter queries are failing, let's try a different RPC or standard logic?
    # Actually, let's just use the w3.eth.get_transaction approach if we knew the hash, but we don't.
    # Let's try scan JUST the last block.
    
    current_block = w3.eth.block_number
    start_block = current_block - 1
    
    print(f"Scanning blocks {start_block} to {current_block}...")
    
    events = contract.events.AgreementCreated.get_logs(from_block=start_block, to_block=current_block)
    
    print(f"Found {len(events)} recent agreements.")
    
    for e in reversed(events):
        args = e['args']
        print(f"--- Agreement Found ---")
        print(f"ID:      {args['agreementId']}")
        print(f"Payer:   {args['payer']}")
        print(f"Payee:   {args['payee']}")
        print(f"Amount:  {w3.from_wei(args['amount'], 'ether')} BNB")
        print(f"TxHash:  {e['transactionHash'].hex()}")
        print("-----------------------")

if __name__ == "__main__":
    check_escrows()
