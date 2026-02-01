import asyncio
import json
from web3 import Web3
from eth_utils import from_wei

# Configuration
HD_HOT_WALLET = '0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce'
TREASURY_WALLET = '0x571E52efc50055d760CEaE2446aE3B469a806279'
ALICE_WALLET = '0x9E0b5FB77dAD5507360BdDdd2746F5B26A446390'

TST_TOKEN = '0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71'

# Polygon Contracts
POLYGON_USDC = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'
POLYGON_USDT = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'

# BSC Contracts
BSC_USDT = '0x55d398326f99059fF775485246999027B3197955'
BSC_USDC = '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'

# RPCs
POLYGON_RPC = "https://polygon-rpc.com"
BSC_RPC = "https://bsc-dataseed1.binance.org"

# Minimal ERC20 ABI
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
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
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

def format_units(value, decimals):
    return value / (10 ** decimals)

def main():
    print("=" * 60)
    print("CITADEL WALLET SYSTEM AUDIT")
    print("=" * 60)

    # Initialize Web3
    w3_poly = Web3(Web3.HTTPProvider(POLYGON_RPC))
    w3_bsc = Web3(Web3.HTTPProvider(BSC_RPC))
    
    # 1. Netflix Wallet (Mock User / Legacy)
    print(f"\n[ WALLET 1 ] Netflix/User ({HD_HOT_WALLET})")
    print("-" * 40)
    try:
        check_bsc_balances(HD_HOT_WALLET, w3_bsc)
        check_polygon_balances(HD_HOT_WALLET, w3_poly)
    except Exception as e:
        print(f"Error: {e}")

    # 2. Treasury (Vault)
    print(f"\n[ WALLET 2 ] Citadel Treasury ({TREASURY_WALLET})")
    print("-" * 40)
    try:
        check_bsc_balances(TREASURY_WALLET, w3_bsc)
    except Exception as e:
        print(f"Error: {e}")

    # 3. Alice (Counterparty)
    print(f"\n[ WALLET 3 ] Alice/Payee ({ALICE_WALLET})")
    print("-" * 40)
    try:
        # Only check TST mostly
        check_tst_only(ALICE_WALLET, w3_bsc)
    except Exception as e:
        print(f"Error: {e}")

def check_tst_only(address, w3):
    tst_contract = w3.eth.contract(address=TST_TOKEN, abi=ERC20_ABI)
    decimals = tst_contract.functions.decimals().call()
    bal = tst_contract.functions.balanceOf(address).call()
    print(f"  ● TST:     {format_units(bal, decimals):,.2f}")

def check_polygon_balances(address, w3):
    print("POLYGON:")
    try:
        # Native MATIC
        matic_wei = w3.eth.get_balance(address)
        print(f"  MATIC:  {w3.from_wei(matic_wei, 'ether'):.6f}")

        # USDC (6 Decimals)
        ctr_usdc = w3.eth.contract(address=POLYGON_USDC, abi=ERC20_ABI)
        bal_usdc = ctr_usdc.functions.balanceOf(address).call()
        print(f"  USDC:   ${format_units(bal_usdc, 6):.2f}")

        # USDT (6 Decimals)
        ctr_usdt = w3.eth.contract(address=POLYGON_USDT, abi=ERC20_ABI)
        bal_usdt = ctr_usdt.functions.balanceOf(address).call()
        print(f"  USDT:   ${format_units(bal_usdt, 6):.2f}")

    except Exception as e:
        print(f"  Error fetching Polygon data: {e}")

def check_bsc_balances(address, w3):
    print("BSC:")
    try:
        # Native BNB
        bnb_wei = w3.eth.get_balance(address)
        print(f"  BNB:    {w3.from_wei(bnb_wei, 'ether'):.6f}")

        # USDT (18 Decimals)
        ctr_bsc_usdt = w3.eth.contract(address=BSC_USDT, abi=ERC20_ABI)
        bal_bsc_usdt = ctr_bsc_usdt.functions.balanceOf(address).call()
        print(f"  USDT:   ${format_units(bal_bsc_usdt, 18):.2f}")

        # USDC (18 Decimals)
        ctr_bsc_usdc = w3.eth.contract(address=BSC_USDC, abi=ERC20_ABI)
        bal_bsc_usdc = ctr_bsc_usdc.functions.balanceOf(address).call()
        print(f"  USDC:   ${format_units(bal_bsc_usdc, 18):.2f}")

        # TST Token (18 Decimals)
        ctr_tst = w3.eth.contract(address=TST_TOKEN, abi=ERC20_ABI)
        bal_tst = ctr_tst.functions.balanceOf(address).call()
        print(f"  TST:    {format_units(bal_tst, 18):,.2f}")

    except Exception as e:
        print(f"  Error fetching BSC data: {e}")

if __name__ == "__main__":
    main()
