import asyncio
from web3 import Web3
from app.core.config import settings
from app.services.access_control import access_control

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------
# USER ID 0 (Derived from your Master Seed)
USER_TO_FUND = "0xb5E7D6AC4753E274d6879fCB44aebDceBE75b970" # azurefashion254@gmail.com
AMOUNT_TST = 100
AMOUNT_BNB = 0.005

# BSC TESTNET CONFIG
RPC_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/"
TST_ADDRESS = "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5"

# --------------------------------------------------------------------------
# SETUP
# --------------------------------------------------------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))
sender_key = settings.DEPLOYER_PRIVATE_KEY
account = w3.eth.account.from_key(sender_key)
sender_address = account.address

ERC20_ABI = [
    {
        "constant": False,
        "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

async def run_faucet():
    print("="*60)
    print("ADMIN FAUCET: FUNDING USER 0 (TESTNET)")
    print(f"Target: {USER_TO_FUND}")
    print("="*60)
    
    if not w3.is_connected():
        print("❌ Cannot connect to BSC Testnet")
        return

    # 1. Check Admin Balances (Gas & Token)
    admin_bnb = w3.eth.get_balance(sender_address)
    contract = w3.eth.contract(address=TST_ADDRESS, abi=ERC20_ABI)
    admin_tst = contract.functions.balanceOf(sender_address).call()
    
    print(f"ADMIN WALLET: {sender_address}")
    print(f"   BNB Balance: {w3.from_wei(admin_bnb, 'ether'):.4f} BNB")
    print(f"   TST Balance: {admin_tst / 10**18:.2f} TST")
    
    if admin_bnb == 0:
        print("❌ Admin has 0 BNB on Testnet. Cannot pay gas.")
        print("👉 Go to: https://testnet.binance.org/faucet-smart")
        return

    # 2. Send BNB (For Gas)
    # DISABLE FOR GAS REFUEL DEMO
    # print("\n[1/2] Sending Gas (BNB)...")
    # try:
    #     tx = {
    #         'nonce': w3.eth.get_transaction_count(sender_address),
    #         'to': USER_TO_FUND,
    #         'value': w3.to_wei(AMOUNT_BNB, 'ether'),
    #         'gas': 21000,
    #         'gasPrice': w3.eth.gas_price,
    #         'chainId': 97
    #     }
    #     signed = w3.eth.account.sign_transaction(tx, sender_key)
    #     tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    #     print(f"   ✅ BNB Sent! TX: {w3.to_hex(tx_hash)}")
    # except Exception as e:
    #     print(f"   ⚠️ BNB Failed: {e}")

    # 3. Send TST (Token)
    print("\n[2/2] Sending Tokens (TST)...")
    try:
        # Wait a sec for nonce update
        await asyncio.sleep(3) 
        
        amount_wei = AMOUNT_TST * 10**18
        tx = contract.functions.transfer(USER_TO_FUND, amount_wei).build_transaction({
            'chainId': 97,
            'gas': 80000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(sender_address)
        })
        signed = w3.eth.account.sign_transaction(tx, sender_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"   ✅ TST Sent! TX: {w3.to_hex(tx_hash)}")
    except Exception as e:
        print(f"   ⚠️ TST Failed: {e}")

        print("Error: Could not connect to BSC.")
        return

    check_tier_before = await access_control.get_user_tier(USER_TO_FUND)
    print(f"Current User Tier: {check_tier_before}")

    tst_contract = w3.eth.contract(address=w3.to_checksum_address(TST_ADDRESS), abi=ERC20_ABI)
    
    # Check Sender BNB Balance
    sender_bnb = w3.eth.get_balance(sender_address)
    print(f"Sender BNB Balance: {w3.from_wei(sender_bnb, 'ether'):.6f} BNB")
    if sender_bnb == 0:
        print("CRITICAL ERROR: Sender has 0 BNB! Cannot pay for gas.")
        return

    # Check Sender Balance
    sender_bal = tst_contract.functions.balanceOf(sender_address).call()
    decimals = tst_contract.functions.decimals().call()
    
    amount_wei = AMOUNT_TST * (10 ** decimals)
    
    print(f"Sender ({sender_address}) Balance: {sender_bal / (10**decimals):,.2f} TST")
    
    if sender_bal < amount_wei:
        print("Error: Master Wallet insufficient balance.")
        return

    # SEND
    print(f"Sending {AMOUNT_TST} TST to {USER_TO_FUND}...")
    
    nonce = w3.eth.get_transaction_count(sender_address)
    tx_data = tst_contract.functions.transfer(
        w3.to_checksum_address(USER_TO_FUND),
        amount_wei
    ).build_transaction({
        'chainId': 97,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx_data, sender_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"Transaction Sent! Hash: {w3.to_hex(tx_hash)}")
    print("Waiting for confirmation...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt['status'] == 1:
        print("Confirmed: SUCCESS (Status 1)")
    else:
        print("Confirmed: FAILED (Status 0). Transaction Reverted!")
        return
    
    # VERIFY NEW TIER
    check_tier_after = await access_control.get_user_tier(USER_TO_FUND)
    print(f"New User Tier: {check_tier_after}")
    
    if check_tier_after != "OBSERVER":
        print("SUCCESS! Feature Unlocked.")

if __name__ == "__main__":
    asyncio.run(run_faucet())
