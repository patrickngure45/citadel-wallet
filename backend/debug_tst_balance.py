from web3 import Web3
from app.core.config import settings

# CONFIG
USER_TO_CHECK = "0x578FC7311a846997dc99bF2d4C651418DcFe309A"
# Use Testnet Address from .env hints or prev context
TST_ADDRESS = "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5" 

# SETUP
# Use Testnet RPC
w3 = Web3(Web3.HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545/"))

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

def debug_user():
    print("="*60)
    print("DEBUGGER: CHECKING ON-CHAIN STATE")
    print("="*60)
    
    if not w3.is_connected():
        print("Error: Could not connect to BSC.")
        return

    print(f"Target User: {USER_TO_CHECK}")
    print(f"Token Contract: {TST_ADDRESS}")
    print("-" * 60)

    # 1. Check Native BNB Balance
    bnb_balance_wei = w3.eth.get_balance(USER_TO_CHECK)
    print(f"Native BNB Balance: {w3.from_wei(bnb_balance_wei, 'ether'):.6f} BNB")

    # 2. Check Contract Code
    code = w3.eth.get_code(w3.to_checksum_address(TST_ADDRESS))
    if len(code) <= 2:
        print("[CRITICAL] No Code at Token Address! Are you on the right chain?")
        return
    else:
        print("[OK] Token Contract exists.")

    # 3. Check Token Balance
    contract = w3.eth.contract(address=w3.to_checksum_address(TST_ADDRESS), abi=ERC20_ABI)
    try:
        raw_balance = contract.functions.balanceOf(w3.to_checksum_address(USER_TO_CHECK)).call()
        decimals = contract.functions.decimals().call()
        human_balance = raw_balance / (10 ** decimals)
        
        print(f"Raw TST Balance: {raw_balance}")
        print(f"Decimals: {decimals}")
        print(f"adjusted TST Balance: {human_balance:,.2f} TST")
        
        if human_balance >= 100:
            print("[PASS] User has enough TST for Standard Tier.")
        else:
            print("[FAIL] User has insufficient TST.")
            
    except Exception as e:
        print(f"[ERROR] Calling contract: {e}")

if __name__ == "__main__":
    debug_user()
