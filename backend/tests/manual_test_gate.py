import requests
import uuid
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_flow():
    # 1. Create User 1 (Should be Index 1 -> Whitelisted)
    email1 = f"test_allow_{int(time.time())}@example.com"
    r1 = requests.post(f"{BASE_URL}/users/", json={"email": email1, "name": "Allowed User"})
    if r1.status_code != 200:
        print(f"Failed to create user 1: {r1.text}")
        return
    user1 = r1.json()
    print(f"User 1 Created: ID={user1['id']}, Index={user1['derivation_index']}")
    
    # 2. Create User 2 (Should be Index 2 -> Blocked)
    email2 = f"test_block_{int(time.time())}@example.com"
    r2 = requests.post(f"{BASE_URL}/users/", json={"email": email2, "name": "Blocked User"})
    if r2.status_code != 200:
        print(f"Failed to create user 2: {r2.text}")
        return
    user2 = r2.json()
    print(f"User 2 Created: ID={user2['id']}, Index={user2['derivation_index']}")
    
    # 3. Test Access for User 1 (Expected: Success)
    print("\n[Testing Whitelisted User]")
    r_access1 = requests.post(f"{BASE_URL}/agreements/{user1['id']}/create")
    if r_access1.status_code == 200:
        print("PASS: User 1 granted access.")
    else:
        print(f"FAIL: User 1 denied access. Status: {r_access1.status_code}, Msg: {r_access1.text}")
        
    # 4. Test Access for User 2 (Expected: 403 Forbidden)
    print("\n[Testing Blocked User]")
    r_access2 = requests.post(f"{BASE_URL}/agreements/{user2['id']}/create")
    if r_access2.status_code == 403:
        print("PASS: User 2 denied access (Correctly gated).")
        print(f"Message: {r_access2.json()['detail']}")
    else:
        print(f"FAIL: User 2 should be denied but got {r_access2.status_code}")

if __name__ == "__main__":
    test_flow()
