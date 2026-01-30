import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_agreement_logic():
    print("=== STARTING AGREEMENT LOGIC TEST ===")
    
    # 1. Create a Whitelisted User (Index 1 is taken, next available low index might be tricky if auto-increment is high)
    # Actually, the logic in users.py uses "next available index". 
    # But access_control.py hardcodes specific ADDRESSES for bypass.
    # So we need to use a specifc address.
    # The bypass list has: 0x578E... (Test User) and 0x578FC... (Index 1).
    
    # We should reuse the user with Index 1 if possible, or created a new one and HOPE it gets a bypass address? 
    # No, new users get new random indices.
    # But wait, access_control.py checks the ADDRESS.
    # So if we can't force the address, we can't bypass unless we own the tokens.
    # LUCKILY: The "Index 1" user likely already exists in the DB from previous runs?
    
    # Let's list users and find the one with index 1?
    # We can't query by index via API easily.
    
    # Alternative: Update the bypass list in access_control.py to include the address of a NEW user we just created.
    # Or, simpler: We just assume the "Test User" from before (User 1 from test_phase0_flow) works?
    # Note: in previous run, User 1 had Index 3. 
    # The whitelisted address 0x578FC... corresponds to Index 1.
    
    # Let's create a new user, get their address, and add it to the bypass list via a temporary file edit? 
    # That's messy.
    
    # Better: Use the endpoints/agreements.py logic update.
    # In my previous edit to agreements.py, I kept the `access_control.check_access` call.
    # And access_control.py has the bypass check.
    
    # Let's try to find the user with Index 1 in the DB?
    # I saw "User: ngurengure10@gmail.com, ID: f5d1f4e6..." in the list.
    # Let's try to use that one.
    
    user_id = "f5d1f4e6-2410-458b-8cd0-a2adcc8e7494" # From debug output
    
    print(f"\n[Test] Using User ID: {user_id}")
    
    # 2. Create Agreement
    print("\n[Test] Creating Agreement...")
    payload = {
        "title": "Dev Test Agreement",
        "counterparty_email": "counterparty@example.com",
        "chain": "bsc",
        "token_symbol": "USDC",
        "amount": 50.0
    }
    
    r = requests.post(f"{BASE_URL}/agreements/{user_id}/create", json=payload)
    if r.status_code == 200:
        agreement = r.json()
        print(f"PASS: Agreement Created! ID: {agreement['id']}")
        print(f"Status: {agreement['status']}")
    else:
        print(f"FAIL: {r.status_code} - {r.text}")
        return

    # 3. List Agreements
    print("\n[Test] Listing Agreements...")
    r_list = requests.get(f"{BASE_URL}/agreements/{user_id}/list")
    if r_list.status_code == 200:
        agreements = r_list.json()
        print(f"PASS: Found {len(agreements)} agreements")
        print(agreements[0])
    else:
        print(f"FAIL: {r_list.status_code} - {r_list.text}")

if __name__ == "__main__":
    test_agreement_logic()
