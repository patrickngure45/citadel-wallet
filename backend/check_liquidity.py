from web3 import Web3
from app.core.config import settings
import json

# BSC RPC
w3 = Web3(Web3.HTTPProvider(settings.BSC_RPC_URL))

# Addresses
PANCAKE_V2_FACTORY = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
PANCAKE_V3_FACTORY = "0x0BFbCF9fa4f9C56B0f40a671Ad2Bd51bdE5252C2"
TST_ADDRESS = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
WBNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
USDT_ADDRESS = "0x55d398326f99059fF775485246999027B3197955"
USDC_ADDRESS = "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"

# Factory ABI (V2 and V3)
FACTORY_ABI_V2 = [
    {
        "constant": True,
        "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "type": "function"
    }
]

FACTORY_ABI_V3 = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"}
        ],
        "name": "getPool",
        "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Pair ABI (Minimal)
PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"}
        ],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    }
]

def check_liquidity():
    print("Checking Liquidity for TST...")
    
    if not w3.is_connected():
        print("Error: Could not connect to BSC Node.")
        return

    chain_id = w3.eth.chain_id
    print(f"Connected to Chain ID: {chain_id}")
    if chain_id == 56:
        print("Network: BSC Mainnet")
    elif chain_id == 97:
        print("Network: BSC Testnet (Addresses above are likely WRONG for Testnet)")
    else:
        print("Network: Unknown")

    check_v2()
    print("-" * 30)
    check_v3()

def check_v2():
    print("Checking PancakeSwap V2...")
    factory = w3.eth.contract(address=w3.to_checksum_address(PANCAKE_V2_FACTORY), abi=FACTORY_ABI_V2)
    
    pairs_to_check = [
        ("USDT", USDT_ADDRESS),
        ("WBNB", WBNB_ADDRESS),
        ("USDC", USDC_ADDRESS)
    ]

    for label, addr in pairs_to_check:
        print(f"Checking TST <-> {label} Pair...")
        pair_addr = factory.functions.getPair(TST_ADDRESS, addr).call()
        
        if pair_addr == "0x0000000000000000000000000000000000000000":
            print(f"   [X] No V2 Pair Found.")
        else:
            print(f"   [!] V2 Pair Found at: {pair_addr}")
            analyze_pair(pair_addr)

def check_v3():
    print("Checking PancakeSwap V3...")
    
    # Verify Factory exists
    factory_addr = w3.to_checksum_address(PANCAKE_V3_FACTORY)
    code = w3.eth.get_code(factory_addr)
    if len(code) <= 2: # "0x"
        print(f"   [CRITICAL] Factory contract not found at {factory_addr} on this chain.")
        return

    factory = w3.eth.contract(address=factory_addr, abi=FACTORY_ABI_V3)
    
    # V3 Fees: 0.01% (100), 0.05% (500), 0.25% (2500), 1% (10000)
    fees = [100, 500, 2500, 10000]

    for fee in fees:
        print(f"Checking TST <-> USDT (Fee: {fee/10000:.2%})...")
        try:
            pool_addr = factory.functions.getPool(
                w3.to_checksum_address(TST_ADDRESS), 
                w3.to_checksum_address(USDT_ADDRESS), 
                fee
            ).call()
            
            if pool_addr != "0x0000000000000000000000000000000000000000":
                 print(f"   [!] V3 Pool Found at: {pool_addr} (Fee: {fee})")
            else:
                print("   [X] No Pool.")
        except Exception as e:
            print(f"   [Error] checking pool: {e}")

    for fee in fees:
        print(f"Checking TST <-> USDC (Fee: {fee/10000:.2%})...")
        try:
            pool_addr = factory.functions.getPool(
                w3.to_checksum_address(TST_ADDRESS), 
                w3.to_checksum_address(USDC_ADDRESS), 
                fee
            ).call()
            
            if pool_addr != "0x0000000000000000000000000000000000000000":
                 print(f"   [!] V3 Pool Found at: {pool_addr} (Fee: {fee})")
            else:
                print("   [X] No Pool.")
        except Exception as e:
            print(f"   [Error] checking pool: {e}")

def analyze_pair(pair_address):
    pair_contract = w3.eth.contract(address=pair_address, abi=PAIR_ABI)
    reserves = pair_contract.functions.getReserves().call()
    token0 = pair_contract.functions.token0().call()
    
    r0 = reserves[0]
    r1 = reserves[1]
    
    # Determine which is TST
    if token0.lower() == TST_ADDRESS.lower():
        tst_res = r0
        other_res = r1
    else:
        tst_res = r1
        other_res = r0

    # Adjust for decimals (Assuming 18 for all for simplicity, usually correct for USDT/BNB/TST)
    tst_human = tst_res / 10**18
    other_human = other_res / 10**18
    
    print(f"   Liquidity Pool Status:")
    print(f"   - TST In Pool: {tst_human:,.2f}")
    print(f"   - Counter Asset: {other_human:,.2f}")
    
    if tst_human > 0:
        price = other_human / tst_human
        print(f"   - Implied Price: {price:.10f} (Counter Asset per TST)")
    else:
        print("   - Pool is EMPTY.")

if __name__ == "__main__":
    check_liquidity()
