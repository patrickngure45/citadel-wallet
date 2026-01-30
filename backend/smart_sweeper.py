import asyncio
import sys
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.services.wallet_service import wallet_service
from app.core.config import settings
from sqlalchemy import select
from web3 import Web3
import json

# --------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------
MASTER_WALLET_ADDRESS = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"
DEPLOYER_PRIVATE_KEY = settings.DEPLOYER_PRIVATE_KEY 

# Tracked Assets
ASSETS = [
    # BSC ASSETS
    {
        "chain": "bsc", 
        "symbol": "USDT", 
        "address": "0x55d398326f99059fF775485246999027B3197955",
        "min_sweep": 1.0 # Only sweep if > $1.00
    },
    {
        "chain": "bsc", 
        "symbol": "USDC", 
        "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        "min_sweep": 1.0
    },
    # POLYGON ASSETS
    {
        "chain": "polygon", 
        "symbol": "USDT", 
        "address": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        "min_sweep": 1.0
    }
]

# --------------------------------------------------------------------------
# GAS PUMP LOGIC
# --------------------------------------------------------------------------
async def fuel_user_wallet(user_address: str, amount_wei: int, chain: str):
    """
    Sends native gas (BNB/MATIC) from the Deployer/Master wallet to the User wallet
    so the user wallet can pay for the token sweep.
    """
    print(f"  [GAS STATION] Pumping {amount_wei} wei to {user_address} on {chain}...")
    
    # We use the raw Web3 logic here to send from our "System Wallet" (Deployer)
    if chain == "bsc":
        w3 = wallet_service.w3_bsc
        chain_id = 56
    elif chain == "polygon":
        w3 = wallet_service.w3_poly
        chain_id = 137
        
    sender_account = w3.eth.account.from_key(DEPLOYER_PRIVATE_KEY)
    sender_addr = sender_account.address
    
    # Buffer: Send 10% extra to be safe
    amount_to_send = int(amount_wei * 1.1)
    
    # Check if System Wallet has funds
    sys_bal = w3.eth.get_balance(sender_addr)
    if sys_bal < amount_to_send:
        print(f"  [CRITICAL] System Wallet Empty! Want {amount_to_send}, Has {sys_bal}")
        return False

    tx = {
        'nonce': w3.eth.get_transaction_count(sender_addr),
        'to': w3.to_checksum_address(user_address),
        'value': amount_to_send,
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'chainId': chain_id
    }
    
    signed = w3.eth.account.sign_transaction(tx, DEPLOYER_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"  [GAS SENT] Hash: {w3.to_hex(tx_hash)}")
    return True

# --------------------------------------------------------------------------
# MAIN SWEEPER LOOP
# --------------------------------------------------------------------------
async def run_smart_sweeper():
    print("="*60)
    print("CITADEL INTELLIGENT ASSET AGGREGATOR")
    print("="*60)
    print(f"Destination: {MASTER_WALLET_ADDRESS}")
    print(f"Tracking: {[a['symbol'] for a in ASSETS]}")
    print("")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Re-generate address to logging
            user_data = wallet_service.generate_evm_address(user.derivation_index)
            user_addr = user_data["address"]
            
            print(f"Checking {user.email} ({user_addr})...")
            
            for asset in ASSETS:
                chain = asset["chain"]
                symbol = asset["symbol"]
                token_addr = asset["address"]
                
                try:
                    # Check Balance First (for Ledger accuracy)
                    balance = wallet_service.get_token_balance(user_addr, token_addr, chain)
                    min_val = asset.get("min_sweep", 0)
                    
                    if balance > 0:
                        if balance < min_val:
                            print(f"  [SKIP] Found {balance} {symbol}, but below threshold ({min_val})")
                            continue

                        # Attempt Transfer
                        result = await wallet_service.transfer_token(
                            from_index=user.derivation_index,
                            to_address=MASTER_WALLET_ADDRESS,
                            token_address=token_addr,
                            chain=chain
                        )
                        
                        if result and result.startswith("0x"):
                            print(f"  [SUCCESS] Swept {balance} {symbol} on {chain}! TX: {result}")
                            
                            # RECORD TRANSACTION IN LEDGER
                            new_tx = Transaction(
                                user_id=user.id,
                                chain=chain,
                                symbol=symbol,
                                amount=balance,
                                type='DEPOSIT',
                                tx_hash=result
                            )
                            session.add(new_tx)
                            await session.commit()
                            print(f"  [LEDGER] Credited {balance} {symbol} to User.")
                            
                        elif result and result.startswith("NEEDS_GAS"):
                            # GAS PUMP TRIGGER
                            needed = int(result.split(":")[1])
                            print(f"  [TRIGGER] Found {symbol} but need Gas: {needed} wei")
                            await fuel_user_wallet(user_addr, needed, chain)
                            print(f"  [INFO] Will retry sweep in next cycle (after gas confirms)")
                    
                except Exception as e:
                    print(f"  [ERROR] {symbol} on {chain}: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_smart_sweeper())
