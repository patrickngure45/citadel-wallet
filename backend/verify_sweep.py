from web3 import Web3

RPC_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/"
TX_HASH = "0xb540a2444b5c540d6cf04575cc1a51ab4c10263844921e450a8e2160435835a0"

def verify_tx():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    try:
        receipt = w3.eth.get_transaction_receipt(TX_HASH)
        print("--- Transaction Receipt ---")
        print(f"Status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")
        print(f"Block Number: {receipt.blockNumber}")
        print(f"Gas Used: {receipt.gasUsed}")
        print(f"From: {receipt['from']}")
        print(f"To: {receipt['to']}")
        
        # Check value if possible (need get_transaction for value)
        tx = w3.eth.get_transaction(TX_HASH)
        val_bnb = w3.from_wei(tx.value, 'ether')
        print(f"Value: {val_bnb} BNB")
        
    except Exception as e:
        print(f"Error checking TX: {e}")

if __name__ == "__main__":
    verify_tx()