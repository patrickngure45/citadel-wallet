import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import solcx

# Add backend dir to python path to find modules if needed
sys.path.append(os.getcwd())

# Load Env explicitly from root if not found
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv() # Fallback to default search

# Configuration
# Use BSC Testnet for this trial deployment
RPC_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/" 
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

if not PRIVATE_KEY:
    print("Error: DEPLOYER_PRIVATE_KEY not found in .env")
    sys.exit(1)

def compile_source(file_path):
    print(f"Compiling {file_path}...")
    with open(file_path, 'r') as f:
        source = f.read()
    
    # Install specific version if needed
    solcx.install_solc('0.8.0')
    
    compiled_sol = solcx.compile_source(
        source,
        output_values=['abi', 'bin'],
        solc_version='0.8.0'
    )
    
    # Get the contract interface (assuming 1 contract per file)
    contract_id = list(compiled_sol.keys())[0]
    contract_interface = compiled_sol[contract_id]
    return contract_interface

def deploy_contract(w3, account, interface, name, args=[], nonce=None):
    print(f"Deploying {name}...")
    Contract = w3.eth.contract(
        abi=interface['abi'],
        bytecode=interface['bin']
    )
    
    # Build Transaction
    if nonce is None:
        nonce = w3.eth.get_transaction_count(account.address)
    construct_txn = Contract.constructor(*args).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign
    signed = w3.eth.account.sign_transaction(construct_txn, private_key=PRIVATE_KEY)
    
    # Send
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Tv sent: {tx_hash.hex()}. Waiting for receipt...")
    
    # Wait
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"✅ {name} Deployed at: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

def main():
    # Setup connection
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0) # Need for BSC
    
    if not w3.is_connected():
        print("Failed to connect to RPC")
        return

    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Deploying from: {account.address}")
    balance = w3.eth.get_balance(account.address)
    print(f"Balance: {w3.from_wei(balance, 'ether')} BNB")
    
    if balance == 0:
        print("⚠️  Warning: Balance is 0. Deployment might fail on Testnet.")
        print("    If you hold real funds, please change RPC_URL in this script to Mainnet.")
    
    # TST already deployed - skip and use existing address
    tst_address = "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5"
    print(f"Using existing TST at: {tst_address}")
    
    # 2. Deploy Escrow
    escrow_interface = compile_source('backend/contracts/CitadelEscrow.sol')
    escrow_address = deploy_contract(w3, account, escrow_interface, "CitadelEscrow")
    
    print("\n" + "="*50)
    print("DEPLOYMENT COMPLETE")
    print("="*50)
    print(f"NEXT_PUBLIC_TST_ADDRESS={tst_address}")
    print(f"NEXT_PUBLIC_ESCROW_ADDRESS={escrow_address}")
    print("="*50)

if __name__ == "__main__":
    main()
