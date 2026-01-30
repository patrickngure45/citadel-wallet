from app.services.wallet_service import wallet_service

def check():
    print("Checking Master Wallet Derivation...")
    
    # Check Index 0
    w0 = wallet_service.generate_evm_address(0)
    print(f"Index 0: {w0['address']}")
    
    # Check Index 1
    w1 = wallet_service.generate_evm_address(1)
    print(f"Index 1: {w1['address']}")
    
    EXPECTED = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"
    
    if w0['address'] == EXPECTED:
        print("[MATCH] Index 0 IS the Master Wallet.")
    else:
        print(f"[MISMATCH] The system thinks Master is {EXPECTED}, but Index 0 is {w0['address']}.")
        print("This means 'payout_from_master' logic might fail if it uses Index 0 key.")

if __name__ == "__main__":
    check()
