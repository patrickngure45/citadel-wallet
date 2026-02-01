import sys
from web3 import Web3

def main():
    rpc_url = "https://bsc-dataseed1.binance.org"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if len(sys.argv) < 2:
        print("Usage: python script.py <tx_hash>")
        return
        
    tx_hash = sys.argv[1]
    
    print(f"Checking TX: {tx_hash}")
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if receipt['status'] == 1:
            print("✅ Status: SUCCESS")
            print(f"Gas Used: {receipt['gasUsed']}")
        else:
            print("❌ Status: FAILED/REVERTED")
    except Exception as e:
        print(f"❓ Receipt not found yet: {e}")

if __name__ == "__main__":
    main()
