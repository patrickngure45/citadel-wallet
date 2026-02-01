
import asyncio
from web3 import Web3
from eth_account import Account
import time

# Configuration
POLYGON_RPC = "https://polygon-mainnet.g.alchemy.com/v2/a-dy4J4WsLejZXeEHWtnB"
USDT_ADDRESS = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"

# Source (The "External" Wallet)
SOURCE_PK = "3106a51490fd02dfb1ef96da660bfb1b19bef24f4a142da073af95d7e45574c3"
SOURCE_ADDR = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"

# Destination (Citadel Treasury)
DEST_ADDR = "0x571E52efc50055d760CEaE2446aE3B469a806279"

# ABI for Transfer
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
     {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    }
]

def sweep_usdt():
    w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon RPC")
        return

    print(f"🔌 Connected to Polygon (Block: {w3.eth.block_number})")

    # 1. Check MATIC for Gas
    matic_balance = w3.eth.get_balance(SOURCE_ADDR)
    print(f"⛽ MATIC Balance: {w3.from_wei(matic_balance, 'ether'):.4f} MATIC")

    if matic_balance == 0:
        print("❌ CRITICAL: No MATIC for Gas. Cannot sweep USDT.")
        print("   Action: Send ~0.1 MATIC to ", SOURCE_ADDR)
        return

    # 2. Check USDT Balance
    usdt_contract = w3.eth.contract(address=USDT_ADDRESS, abi=ERC20_ABI)
    usdt_bal_raw = usdt_contract.functions.balanceOf(SOURCE_ADDR).call()
    decimals = usdt_contract.functions.decimals().call()
    usdt_bal_readable = usdt_bal_raw / (10 ** decimals)
    
    print(f"💰 USDT Balance: {usdt_bal_readable:.2f} USDT")

    if usdt_bal_raw == 0:
        print("⚠️ No USDT to sweep.")
        return

    # 3. Build Transaction
    print(f"🔄 Preparing to sweep {usdt_bal_readable} USDT -> {DEST_ADDR[:6]}...")
    
    nonce = w3.eth.get_transaction_count(SOURCE_ADDR)
    
    tx = usdt_contract.functions.transfer(
        DEST_ADDR,
        usdt_bal_raw
    ).build_transaction({
        'chainId': 137,
        'gas': 100000, # Conservative limit for ERC20 transfer
        'maxFeePerGas': w3.to_wei('50', 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei('40', 'gwei'),
        'nonce': nonce,
    })

    # 4. Sign
    signed_tx = w3.eth.account.sign_transaction(tx, SOURCE_PK)
    
    # 5. Send
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Transaction Sent! Hash: {w3.to_hex(tx_hash)}")
        print(f"🔗 Tracker: https://polygonscan.com/tx/{w3.to_hex(tx_hash)}")
    except Exception as e:
        print(f"❌ Transaction Failed: {e}")

if __name__ == "__main__":
    sweep_usdt()
