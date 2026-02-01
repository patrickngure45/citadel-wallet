import sys
from web3 import Web3

def main():
    rpc_url = "https://bsc-dataseed1.binance.org"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    ESCROW_ADDRESS = "0x922bA3bD7866F92F0Caa2A544bb303A38922fb12"
    
    abi = [{
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "agreements",
        "outputs": [
            {"internalType": "address", "name": "payer", "type": "address"},
            {"internalType": "address", "name": "payee", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "string", "name": "description", "type": "string"},
            {"internalType": "uint8", "name": "status", "type": "uint8"},
            {"internalType": "uint256", "name": "createdAt", "type": "uint256"},
            {"internalType": "uint256", "name": "completedAt", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }]
    
    contract = w3.eth.contract(address=ESCROW_ADDRESS, abi=abi)
    
    try:
        data = contract.functions.agreements(2).call()
        print(f"Agreement #2:")
        print(f"  Payer: {data[0]}")
        print(f"  Payee: {data[1]}")
        print(f"  Amount: {data[2]}")
        print(f"  Status: {data[4]} (0=Created, 1=Funded, 2=Released, 3=Refunded, 4=Cancelled)")
        
        # Check Treasury Address matching
        treasury = "0x571E52efc50055d760CEaE2446aE3B469a806279"
        if data[0].lower() == treasury.lower():
            print("✅ Payer matches Treasury")
        else:
            print(f"❌ Payer mismatch! Expected {treasury}, got {data[0]}")
            
    except Exception as e:
        print(f"Error reading agreement: {e}")

if __name__ == "__main__":
    main()
