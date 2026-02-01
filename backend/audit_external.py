import asyncio
from app.services.wallet_service import wallet_service
from app.core.config import settings

# 0. TARGET ADDRESS (From your script)
TARGET_ADDRESS = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"

# 1. CONTRACTS CONFIG
# BSC
BSC_TST  = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
BSC_USDT = "0x55d398326f99059fF775485246999027B3197955"
BSC_USDC = "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"

# POLYGON
POLY_USDC = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
POLY_USDT = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"

# ABI
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

async def check_contract(w3, contract_addr, target_addr, label, decimals_override=None):
    if not w3.is_connected():
        print(f"   ❌ {label}: Provider Disconnected")
        return 0.0
        
    try:
        contract = w3.eth.contract(address=contract_addr, abi=ERC20_ABI)
        raw_bal = contract.functions.balanceOf(target_addr).call()
        
        if decimals_override:
            decimals = decimals_override
        else:
            try:
                decimals = contract.functions.decimals().call()
            except:
                decimals = 18
                
        readable = raw_bal / (10 ** decimals)
        prefix = "$" if "USD" in label else ""
        print(f"   {label.ljust(10)}: {prefix}{readable:,.2f}")
        return readable
    except Exception as e:
        print(f"   ⚠️ {label}: Error ({str(e)[:20]}...)")
        return 0.0

async def main():
    print("="*60)
    print("TRADESYNAPSE - TOTAL BALANCE AUDIT (PYTHON PORT)")
    print("="*60)
    print(f"\n📍 TARGET: {TARGET_ADDRESS}")
    
    # -----------------------------------------------------
    # 1. POLYGON SCAN
    # -----------------------------------------------------
    print("\n🟣 POLYGON NETWORK Search...")
    print("-" * 30)
    w3_poly = wallet_service.w3_poly
    
    # Native MATIC
    try:
        matic = w3_poly.eth.get_balance(TARGET_ADDRESS)
        print(f"   MATIC     : {w3_poly.from_wei(matic, 'ether'):,.6f}")
    except:
        print("   MATIC     : [Connection Failed]")

    # Tokens
    total_poly_usd = 0.0
    total_poly_usd += await check_contract(w3_poly, POLY_USDC, TARGET_ADDRESS, "USDC", 6)
    total_poly_usd += await check_contract(w3_poly, POLY_USDT, TARGET_ADDRESS, "USDT", 6)

    # -----------------------------------------------------
    # 2. BSC SCAN
    # -----------------------------------------------------
    print("\n🟡 BSC NETWORK Search...")
    print("-" * 30)
    w3_bsc = wallet_service.w3_bsc
    
    # Native BNB
    try:
        bnb = w3_bsc.eth.get_balance(TARGET_ADDRESS)
        print(f"   BNB       : {w3_bsc.from_wei(bnb, 'ether'):,.6f}")
    except:
        print("   BNB       : [Connection Failed]")
        
    # Tokens
    total_bsc_usd = 0.0
    total_bsc_usd += await check_contract(w3_bsc, BSC_USDT, TARGET_ADDRESS, "USDT", 18)
    total_bsc_usd += await check_contract(w3_bsc, BSC_USDC, TARGET_ADDRESS, "USDC", 18)
    
    await check_contract(w3_bsc, BSC_TST, TARGET_ADDRESS, "TST", 18)
    
    # TST Supply
    try:
        tst_contract = w3_bsc.eth.contract(address=BSC_TST, abi=ERC20_ABI)
        supply = tst_contract.functions.totalSupply().call()
        print(f"\n   TST SUPPLY : {supply / 10**18:,.2f}")
    except:
        pass

    # -----------------------------------------------------
    # 3. SUMMARY
    # -----------------------------------------------------
    total_stable = total_poly_usd + total_bsc_usd
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"TOTAL ON-CHAIN STABLECOINS: ${total_stable:,.2f}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
