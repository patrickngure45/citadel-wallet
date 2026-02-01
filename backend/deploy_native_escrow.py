import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import solcx

# Add backend dir to python path
sys.path.append(os.getcwd())

# Load Env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration: BSC MAINNET
RPC_URL = "https://bsc-dataseed1.binance.org"
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

if not PRIVATE_KEY:
    print("Error: DEPLOYER_PRIVATE_KEY not found in .env")
    sys.exit(1)

# Connect to BSC
w3 = Web3(Web3.HTTPProvider(RPC_URL))
# For BSC, we often need the PoA middleware
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

if not w3.is_connected():
    print("Failed to connect to BSC Mainnet")
    sys.exit(1)

print(f"Connected to BSC Mainnet. Chain ID: {w3.eth.chain_id}")
account = w3.eth.account.from_key(PRIVATE_KEY)
print(f"Deployer Address: {account.address}")
balance = w3.eth.get_balance(account.address)
print(f"Balance: {w3.from_wei(balance, 'ether')} BNB")

# Compile
print("Compiling CitadelEscrow.sol...")
contracts_dir = Path(__file__).parent / "contracts"
contract_path = contracts_dir / "CitadelEscrow.sol"

# Install solc if needed
try:
    solcx.install_solc('0.8.0')
except:
    pass

compiled = solcx.compile_files(
    [str(contract_path)],
    output_values=["abi", "bin"],
    solc_version='0.8.0'
)

# CitadelEscrow.sol might have multiple contracts, get the main one
contract_id = f"{contract_path}:CitadelEscrow"
if contract_id not in compiled:
     # Fallback to key search
    contract_id = [k for k in compiled.keys() if "CitadelEscrow" in k][0]

contract_interface = compiled[contract_id]

# Deploy
print("Deploying contract...")
CitadelEscrow = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

# Build transaction
construct_txn = CitadelEscrow.constructor().build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gasPrice': w3.eth.gas_price,
})

# Estimated gas
try:
    gas_estimate = w3.eth.estimate_gas(construct_txn)
    construct_txn['gas'] = int(gas_estimate * 1.1)
except Exception as e:
    print(f"Gas estimation failed: {e}")
    construct_txn['gas'] = 2000000

# Sign and Send
signed_txn = w3.eth.account.sign_transaction(construct_txn, private_key=PRIVATE_KEY)
print("Sending transaction...")
try:
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    # Wait for receipt
    print("Waiting for confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("-------------------------------------------")
    print(f"✅ Contract Deployed to: {tx_receipt.contractAddress}")
    print("-------------------------------------------")

    # Verify logic (optional, just print the address for contracts.ts)
    print(f"Please update 'ESCROW' in frontend/src/lib/contracts.ts with: {tx_receipt.contractAddress}")

except Exception as e:
    print(f"Deployment failed: {e}")
