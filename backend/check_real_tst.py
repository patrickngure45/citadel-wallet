
from web3 import Web3

# Config
BSC_RPC = "https://bsc-dataseed1.binance.org"
TST_ADDR = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71" # Mainnet TST
TREASURY = "0x571E52efc50055d760CEaE2446aE3B469a806279"

ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"}
]

def check_tst():
    try:
        w3 = Web3(Web3.HTTPProvider(BSC_RPC))
        contract = w3.eth.contract(address=TST_ADDR, abi=ERC20_ABI)
        
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        
        print(f"✅ Contract Found: {symbol} ({TST_ADDR})")
        
        bal_raw = contract.functions.balanceOf(TREASURY).call()
        bal_readable = bal_raw / (10 ** decimals)
        
        print(f"💰 Treasury Balance: {bal_readable:,.2f} {symbol}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_tst()
