import asyncio
from app.services.wallet_service import wallet_service
from app.services.cex_service import cex_service
from app.core.config import settings

# 1. DEPLOYER ADDRESS (From Private Key)
DEPLOYER_ADDRESS = "0x571E52efc50055d760CEaE2446aE3B469a806279"

# 2. MASTER DERIVATION ADDRESS (Index 0 from Seed)
# "produce dice skin..." -> Index 0
# Previous scripts derived: 0x578FC7311a846997dc99bF2d4C651418DcFe309A
# Let's verify both.
MASTER_VAULT = "0x578FC7311a846997dc99bF2d4C651418DcFe309A"

WALLETS = {
    "Deployer (Admin)": DEPLOYER_ADDRESS,
    "Master Vault (Seed #0)": MASTER_VAULT
}

# Common Token Contracts on Ethereum (Mainnet)
TOKENS = {
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA"
}

# ABI for checking balance (Minimal)
ERC20_ABI = [
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
        "type": "function"
    }
]

async def check_balances():
    print(f"\n📊 DEEP-SCAN WALLET AUDIT")
    print("=" * 60)
    
    # --- PART 1: ON-CHAIN WALLETS ---
    for name, address in WALLETS.items():
        print(f"🏰 {name}: {address}")
        print("-" * 30)
        
        # 1. Native ETH
        w3_eth = wallet_service.w3_eth
        try:
            eth_bal = w3_eth.eth.get_balance(address)
            print(f"   ETH (Mainnet):  {w3_eth.from_wei(eth_bal, 'ether'):.6f} ETH")
        except Exception as e:
            print(f"   ETH:            [Connection Failed]")

        # 2. Native BNB
        w3_bsc = wallet_service.w3_bsc
        try:
            bnb_bal = w3_bsc.eth.get_balance(address)
            print(f"   BNB (BSC):      {w3_bsc.from_wei(bnb_bal, 'ether'):.6f} BNB")
        except Exception as e:
            print(f"   BNB:            [Connection Failed]")

        # 3. Native MATIC (Polygon)
        w3_poly = wallet_service.w3_poly
        try:
            matric_bal = w3_poly.eth.get_balance(address)
            print(f"   MATIC (Poly):   {w3_poly.from_wei(matric_bal, 'ether'):.6f} MATIC")
        except Exception as e:
            print(f"   MATIC:          [Connection Failed]")

        # 4. Tokens (ETH Mainnet)
        for symbol, contract_address in TOKENS.items():
            try:
                contract = w3_eth.eth.contract(address=contract_address, abi=ERC20_ABI)
                raw_balance = contract.functions.balanceOf(address).call()
                # Handle decimals carefully or default to 18
                try:
                    decimals = contract.functions.decimals().call()
                except:
                    decimals = 18
                    
                readable_balance = raw_balance / (10 ** decimals)
                if readable_balance > 0:
                     print(f"   ✨ {symbol} (ETH):  {readable_balance:,.6f}")
            except Exception:
                pass 
        print("-" * 60)

    # --- PART 2: OFF-CHAIN CEX ---
    print("🏦 Centralized Exchange (Binance)")
    
    if settings.BINANCE_API_KEY:
        try:
             # Use the service to fetch real balances
             balances = await cex_service.get_user_balance("binance", settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)
             
             if not balances:
                 print("   [Monitoring Active: No Assets Detected]")
             else:
                 for asset, amount in balances.items():
                     print(f"   💰 {asset}: {amount:,.8f}")
                     
        except Exception as e:
             print(f"   [Error Fetching CEX: {e}]")
    else:
        print("   [No API Keys Configured]")
        
    print("=" * 60)
    print("✅ Audit Complete\n")

if __name__ == "__main__":
    asyncio.run(check_balances())
