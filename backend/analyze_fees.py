import sys
from web3 import Web3

def main():
    rpc_url = "https://bsc-dataseed1.binance.org"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    tx_hash = "0x554efbc91fa3a03dcb950dfbc92d5ee9406b6a9b6954e7949d445a5e59c3d727"
    
    print(f"🔍 Analyzing Release TX: {tx_hash}")
    
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except Exception as e:
        print(f"Error fetching receipt: {e}")
        return

    # ERC20 Transfer Event Signature
    # event Transfer(address indexed from, address indexed to, uint256 value);
    transfer_event_hash = w3.keccak(text="Transfer(address,address,uint256)").hex()
    
    print(f"\n🪙 Token Transfers found in logs:")
    
    transfer_count = 0
    tst_contract = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
    
    for i, log in enumerate(receipt['logs']):
        # Check if it matches Transfer event signature
        if log['topics'][0].hex() == transfer_event_hash:
            transfer_count += 1
            
            # Decode params
            token_address = log['address']
            src = w3.to_checksum_address("0x" + log['topics'][1].hex()[-40:])
            dst = w3.to_checksum_address("0x" + log['topics'][2].hex()[-40:])
            val = int(log['data'].hex(), 16)
            
            # Is this TST?
            token_name = "UNKNOWN"
            if token_address.lower() == tst_contract.lower():
                token_name = "TST"
                val_fmt = val / 10**18
            else:
                val_fmt = val
                
            print(f"  [{i}] Token: {token_name} ({token_address})")
            print(f"      From: {src}")
            print(f"      To:   {dst}")
            print(f"      Amt:  {val_fmt:,.2f}")
            print("-" * 40)

    if transfer_count == 0:
        print("❌ No Transfer events found.")

if __name__ == "__main__":
    main()
