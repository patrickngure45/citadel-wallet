
import asyncio
from web3 import Web3
from eth_abi import encode

# Polygon RPC
POLYGON_RPC = "https://polygon-mainnet.g.alchemy.com/v2/a-dy4J4WsLejZXeEHWtnB"
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

# Wallets
EXTERNAL_WALLET = Web3.to_checksum_address("0xf5C607833501625D4223A44F3d582afB9772D931") # The one with ~10 USDT
TREASURY = Web3.to_checksum_address("0x571E52efc50055d760CEaE2446aE3B469a806279")      # The Admin/Treasury

# USDT Contract on Polygon
USDT_ADDR = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"

# Minimal ABI for balanceOf
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    }
]

def check_balance(name, address):
    try:
        contract = w3.eth.contract(address=USDT_ADDR, abi=ERC20_ABI)
        balance = contract.functions.balanceOf(address).call()
        decimals = contract.functions.decimals().call()
        readable = balance / (10 ** decimals)
        print(f"💰 {name} ({address[:6]}...): {readable:.2f} USDT")
        return readable
    except Exception as e:
        print(f"❌ Error checking {name}: {e}")
        return 0

def main():
    print("Searching for the missing $9...")
    
    # 1. Check the Source (External Wallet)
    ext_bal = check_balance("Old External Wallet", EXTERNAL_WALLET)
    
    # 2. Check the Destination (Treasury)
    treasury_bal = check_balance("Citadel Treasury", TREASURY)
    
    if ext_bal > 1.0:
        print("\n✅ FOUND IT: The money is still in the External Wallet.")
        print("   It has not been evacuated yet because the 'Evacuate' command")
        print("   currently targets Binance (CEX), not on-chain wallets.")
    elif treasury_bal > 1.0:
        print("\n✅ FOUND IT: It arrived safely in the Citadel Treasury!")
    else:
        print("\n❓ MYSTERY: It's not in either. Validating other addresses...")

if __name__ == "__main__":
    main()
