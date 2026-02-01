
from web3 import Web3

# Config
ADDR = "0x571E52efc50055d760CEaE2446aE3B469a806279"
BSC_MAINNET = "https://bsc-dataseed1.binance.org"
BSC_TESTNET = "https://data-seed-prebsc-1-s1.binance.org:8545"

def check(url, name):
    try:
        w3 = Web3(Web3.HTTPProvider(url))
        if w3.is_connected():
            bal = w3.eth.get_balance(ADDR)
            readable = w3.from_wei(bal, 'ether')
            print(f"[{name}] Balance: {readable:.4f} BNB")
            return readable
        else:
            print(f"[{name}] Connection Failed")
            return 0
    except Exception as e:
        print(f"[{name}] Error: {e}")
        return 0

if __name__ == "__main__":
    print(f"🔎 Auditing Treasury: {ADDR}")
    m = check(BSC_MAINNET, "BSC MAINNET")
    t = check(BSC_TESTNET, "BSC TESTNET")
    
    if m > 0:
        print("\n✅ We have REAL GAS on Mainnet. We can build live.")
    elif t > 0:
        print("\n✅ We have TEST GAS. We can simulate everything.")
    else:
        print("\n❌ We are completely out of gas on both networks.")
