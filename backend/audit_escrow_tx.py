import os
import sys
from web3 import Web3

def main():
    # Setup Web3 for BSC Mainnet
    rpc_url = "https://bsc-dataseed1.binance.org"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    tx_hash = "0x1be862f4e11492bed2a72bfca4c026e8889472ccce26c97c46b0ff239ad0ade3"
    print(f"🔍 Analyzing TX: {tx_hash}")
    
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except Exception as e:
        print(f"Error fetching receipt: {e}")
        return

    # TSTEscrow Contract Event Signature
    # event AgreementCreated(uint256 indexed agreementId, address indexed payer, address indexed payee, uint256 amount, string description);
    event_signature_hash = w3.keccak(text="AgreementCreated(uint256,address,address,uint256,string)").hex()
    
    found = False
    for log in receipt['logs']:
        if log['topics'][0].hex() == event_signature_hash:
            # Topic 1: agreementId (indexed)
            agreement_id = int(log['topics'][1].hex(), 16)
            
            # Topic 2: payer (indexed)
            payer = w3.to_checksum_address("0x" + log['topics'][2].hex()[-40:])
            
            # Topic 3: payee (indexed)
            payee = w3.to_checksum_address("0x" + log['topics'][3].hex()[-40:])
            
            print(f"\n✅ FOUND AGREEMENT CREATED EVENT")
            print(f"🆔 Agreement ID: {agreement_id}")
            print(f"👤 Payer:        {payer}")
            print(f"👤 Payee:        {payee}")
            found = True
            
    if not found:
        print("❌ No creation event found in logs.")

if __name__ == "__main__":
    main()
