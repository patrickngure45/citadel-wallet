
from eth_account import Account
# import mnemo  <-- removed unused import
from web3 import Web3

# The seed from your provided .env
MNEMONIC = "produce dice skin segment album section group lawn cup wisdom rich frequent pledge bright cage barrel demise sell sunset picnic lend post race pact"
TARGET_ADDRESS = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"

def check_derivation():
    Account.enable_unaudited_hdwallet_features()
    
    print(f"🔍 Checking if {TARGET_ADDRESS[:6]}... belongs to this seed...")
    
    found = False
    for i in range(20):
        # Derivation path: m/44'/60'/0'/0/i
        path = f"m/44'/60'/0'/0/{i}"
        acct = Account.from_mnemonic(MNEMONIC, account_path=path)
        
        print(f"Index {i}: {acct.address}")
        
        if acct.address.lower() == TARGET_ADDRESS.lower():
            print(f"\n✅ MATCH FOUND at Index {i}!")
            print(f"   Private Key: {acct.key.hex()}")
            found = True
            break
            
    if not found:
        print("\n❌ No match found in first 20 indices.")
        print("   This means that wallet was created with a DIFFERENT seed phrase.")

if __name__ == "__main__":
    check_derivation()
