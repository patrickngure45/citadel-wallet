import asyncio
import json
from web3 import Web3
from eth_utils import from_wei

# Configuration
HD_HOT_WALLET = '0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce'
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
    print("=" * 50)
    print("TRADESYNAPSE - TOTAL BALANCE CHECK (PYTHON PORT)")
    print("=" * 50)
    print("")

    print("1. ON-CHAIN BALANCES (HD Hot Wallet)")
    print("-" * 40)
    print(f"Address: {HD_HOT_WALLET}")
    print("")

    # Initialize Web3
    w3_poly = Web3(Web3.HTTPProvider(POLYGON_RPC))
    w3_bsc = Web3(Web3.HTTPProvider(BSC_RPC))

    # ---------------------------------------------------------
    # POLYGON CHECK
    # ---------------------------------------------------------
    print("POLYGON:")
    try:
        # Native MATIC
        matic_wei = w3_poly.eth.get_balance(HD_HOT_WALLET)
        print(f"  MATIC:  {w3_poly.from_wei(matic_wei, 'ether'):.6f}")

        # USDC (6 Decimals)
        ctr_usdc = w3_poly.eth.contract(address=POLYGON_USDC, abi=ERC20_ABI)
        bal_usdc = ctr_usdc.functions.balanceOf(HD_HOT_WALLET).call()
        print(f"  USDC:   ${format_units(bal_usdc, 6):.2f}")

        # USDT (6 Decimals)
        ctr_usdt = w3_poly.eth.contract(address=POLYGON_USDT, abi=ERC20_ABI)
        bal_usdt = ctr_usdt.functions.balanceOf(HD_HOT_WALLET).call()
        print(f"  USDT:   ${format_units(bal_usdt, 6):.2f}")
        
        poly_usd_total = format_units(bal_usdc, 6) + format_units(bal_usdt, 6)

    except Exception as e:
        print(f"  Error fetching Polygon data: {e}")
        poly_usd_total = 0

    print("")

    # ---------------------------------------------------------
    # BSC CHECK
    # ---------------------------------------------------------
    print("BSC:")
    try:
        # Native BNB
        bnb_wei = w3_bsc.eth.get_balance(HD_HOT_WALLET)
        print(f"  BNB:    {w3_bsc.from_wei(bnb_wei, 'ether'):.6f}")

        # USDT (18 Decimals on BSC usually, checking script assumption)
        # Script said formatUnits(usdtBsc, 18)
        ctr_bsc_usdt = w3_bsc.eth.contract(address=BSC_USDT, abi=ERC20_ABI)
        bal_bsc_usdt = ctr_bsc_usdt.functions.balanceOf(HD_HOT_WALLET).call()
        print(f"  USDT:   ${format_units(bal_bsc_usdt, 18):.2f}")

        # USDC (18 Decimals on BSC)
        ctr_bsc_usdc = w3_bsc.eth.contract(address=BSC_USDC, abi=ERC20_ABI)
        bal_bsc_usdc = ctr_bsc_usdc.functions.balanceOf(HD_HOT_WALLET).call()
        print(f"  USDC:   ${format_units(bal_bsc_usdc, 18):.2f}")

        # TST Token (18 Decimals)
        ctr_tst = w3_bsc.eth.contract(address=TST_TOKEN, abi=ERC20_ABI)
        bal_tst = ctr_tst.functions.balanceOf(HD_HOT_WALLET).call()
        print(f"  TST:    {format_units(bal_tst, 18):.6f}")

        bsc_usd_total = format_units(bal_bsc_usdt, 18) + format_units(bal_bsc_usdc, 18)

        # Total Supply
        tst_supply = ctr_tst.functions.totalSupply().call()
        
    except Exception as e:
        print(f"  Error fetching BSC data: {e}")
        bsc_usd_total = 0
        tst_supply = 0

    print("")

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    total_on_chain = poly_usd_total + bsc_usd_total
    
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"On-Chain Stablecoins: ${total_on_chain:.2f}")
    if tst_supply > 0:
        print(f"TST Token Supply:     {format_units(tst_supply, 18):,.2f} TST")
    print("=" * 50)

if __name__ == "__main__":
    main()
