import asyncio
import sys
import uuid
from datetime import datetime
from app.db.session import AsyncSessionLocal
from app.models.hearing import HearingRecordModel
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.services.wallet_service import wallet_service
from app.core.config import settings
from app.entities.arena import Arena
from sqlalchemy import select, func
from web3 import Web3
import json

# --------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------
# The "Citadel" Cold Storage / Admin Hub
MASTER_WALLET_ADDRESS = "0x571E52efc50055d760CEaE2446aE3B469a806279"
DEPLOYER_PRIVATE_KEY = settings.DEPLOYER_PRIVATE_KEY 

# Tracked Assets
ASSETS = [
    # BSC TESTNET ASSETS (Trial Mode)
    {
        "chain": "bsc_testnet", 
        "symbol": "TST", 
        "address": "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5",
        "min_sweep": 1.0 # Sweep if > 1 TST
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
    w3 = None
    chain_id = 0
    
    if chain == "bsc":
        w3 = wallet_service.w3_bsc
        chain_id = 56
    elif chain == "polygon":
        w3 = wallet_service.w3_poly
        chain_id = 137
    elif chain == "bsc_testnet":
        w3 = wallet_service.w3_bsc_testnet
        chain_id = 97
        
    if not w3:
        print(f"  [ERROR] Unknown chain for gas pump: {chain}")
        return False
        
    sender_account = w3.eth.account.from_key(DEPLOYER_PRIVATE_KEY)
    sender_addr = sender_account.address
    
    # Buffer: Send 10% extra to be safe
    amount_to_send = int(amount_wei * 1.1)
    
    # Check if System Wallet has funds
    sys_bal = w3.eth.get_balance(sender_addr)
    if sys_bal < amount_to_send:
        print(f"  [CRITICAL] System Wallet Empty! Want {amount_to_send} wei, Has {sys_bal}")
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
    print("WITH AGENT ARENA INTEGRATION")
    print("="*60)
    print(f"Destination: {MASTER_WALLET_ADDRESS}")
    print(f"Tracking: {[a['symbol'] for a in ASSETS]}")
    print("Starting Continuous Loop (Press Ctrl+C to stop)...")
    print("")

    arena = Arena()
    
    # State tracking to prevent infinite loops on simulated assets
    # Format: { "user_addr:chain:symbol": last_known_balance }
    known_balances = {}

    while True:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User))
                users = result.scalars().all()
                
                for user in users:
                    # Re-generate address to logging
                    user_data = wallet_service.generate_evm_address(user.derivation_index)
                    user_addr = user_data["address"]
                    
                    # Only print verbose scans if something was found in previous runs logic
                    # For cleanliness, we'll keep it simple
                    # print(f"Scanning {user.email} ({user_addr})...")
                    
                    for asset in ASSETS:
                        chain = asset["chain"]
                        symbol = asset["symbol"]
                        token_addr = asset["address"]
                        
                        # Unique Key for this asset/user combo
                        cache_key = f"{user_addr}:{chain}:{symbol}"
                        
                        try:
                            # 1. PERCEPTION CHECK (Manual for speed before invoking AI)
                            balance = wallet_service.get_token_balance(user_addr, token_addr, chain)
                            min_val = asset.get("min_sweep", 0)
                            
                            if balance > 0:
                                # CHECK MEMORY: Have we already swept this exact amount?
                                last_bal = known_balances.get(cache_key, -1.0)
                                if balance == last_bal:
                                    # We already processed this balance. 
                                    # Since it hasn't changed, the previous action was likely a simulation 
                                    # or the chain hasn't updated yet. Skip to avoid spam.
                                    continue
                                
                                if balance < min_val:
                                    # print(f"  [SKIP] Found {balance} {symbol}, but below threshold ({min_val})")
                                    continue
                                
                                print(f"  [DETECTED] {balance} {symbol}. Checking Gas...")

                                # Update memory so we don't loop if this fails or is simulated
                                known_balances[cache_key] = balance

                                # 2. GAS CHECK
                                # We need about 100k gas to move a token
                                GAS_LIMIT = 100000
                                w3 = wallet_service.w3_bsc_testnet if chain == "bsc_testnet" else wallet_service.w3_bsc
                                gas_price = w3.eth.gas_price
                                native_needed = GAS_LIMIT * gas_price
                                native_balance = w3.eth.get_balance(user_addr)
                                
                                if native_balance < native_needed:
                                    print(f"  [NEEDS GAS] Has {native_balance} wei, Needs {native_needed} wei")
                                    amount_needed = native_needed - native_balance
                                    await fuel_user_wallet(user_addr, amount_needed, chain)
                                    
                                    # Log Gas Action to Dashboard
                                    time_res = await session.execute(select(func.now()))
                                    db_now_gas = time_res.scalar()
                                    
                                    gas_record = HearingRecordModel(
                                        id=uuid.uuid4(),
                                        user_id=user.id,
                                        intent=f"AUTOPILOT: Refuel Gas ({symbol})",
                                        started_at=db_now_gas,
                                        transcript={"note": f"Pumped {amount_needed} wei to {user_addr}"},
                                        final_verdict="EXECUTED",
                                        final_reason="Gas Required operations"
                                    )
                                    session.add(gas_record)
                                    await session.commit()
                                    
                                    print("  [WAIT] Gas pumping initiated. Skipping for this cycle.")
                                    continue

                                # 3. INVOKE ARENA (The Agent)
                                # We use a structured intent so the Agent knows exactly what to do
                                # This creates the HearingRecord for the dashboard
                                intent_str = f"AUTOPILOT: Sweep all {symbol} to {MASTER_WALLET_ADDRESS}"
                                print(f"  [INVOKING AGENT] Intent: {intent_str}")

                                record = await arena.conduct_hearing(
                                    user_id=str(user.id),
                                    intent=intent_str,
                                    execute=True
                                )

                                # 4. PROCESS RESULT
                                if record.final_verdict == "ALLOWED" and record.execution and record.execution.status == "SUCCESS":
                                    tx_hash = record.execution.tx_hash
                                    print(f"  [SUCCESS] Agent Executed Sweep! TX: {tx_hash}")
                                    
                                    # 5. CREDIT USER LEDGER
                                    # The Agent moved funds, now we credit the user's internal balance
                                    new_tx = Transaction(
                                        user_id=user.id,
                                        chain=chain,
                                        symbol=symbol,
                                        amount=balance,
                                        type='DEPOSIT',
                                        tx_hash=tx_hash
                                    )
                                    session.add(new_tx)
                                    
                                    # Using global import
                                    hearing_db = HearingRecordModel(
                                        id=uuid.UUID(record.id),
                                        user_id=user.id,
                                        intent=record.intent,
                                        started_at=record.started_at,
                                        transcript=record.model_dump(mode='json'),
                                        final_verdict=record.final_verdict,
                                        final_reason=record.final_reason or "Autopilot Success"
                                    )
                                    session.add(hearing_db)

                                    await session.commit()
                                    print(f"  [LEDGER] Credited {balance} {symbol} to User and Logged Hearing.")
                                
                                else:
                                    print(f"  [FAILURE] Agent Execution Failed: {record.final_reason}")
                                    # Log failure too for visibility
                                    hearing_db = HearingRecordModel(
                                        id=uuid.UUID(record.id),
                                        user_id=user.id,
                                        intent=record.intent,
                                        started_at=record.started_at,
                                        transcript=record.model_dump(mode='json'),
                                        final_verdict=record.final_verdict,
                                        final_reason=record.final_reason or "Autopilot Failed"
                                    )
                                    session.add(hearing_db)
                                    await session.commit()

                        except Exception as e:
                            print(f"  [ERROR] {symbol} on {chain}: {e}")
                            import traceback
                            traceback.print_exc()
                        except asyncio.CancelledError:
                            print(f"  [WARNING] Task Cancelled for {symbol}. Retrying next loop.")
                        except BaseException as be:
                            print(f"  [CRITICAL] Unexpected Error: {be}")
                
                # HEARTBEAT LOGGING
                # Use DB time for consistency
                time_res = await session.execute(select(func.now()))
                db_now = time_res.scalar()
                
                print(f"  [SYSTEM] Heartbeat sent at {db_now} (DB Time)...")
                
                sys_id = users[0].id if users else uuid.UUID("00000000-0000-0000-0000-000000000000")
                
                heartbeat = HearingRecordModel(
                        id=uuid.uuid4(),
                        user_id=sys_id,
                        intent="AUTOPILOT: SYSTEM SCAN COMPLETED",
                        started_at=db_now,
                        transcript={"note": "Routine availability check"},
                        final_verdict="ALLOWED",
                        final_reason="Routine Maintenance"
                )
                session.add(heartbeat)
                await session.commit()

        except Exception as e:
            print(f"Loop Error: {e}")
        
        # Wait 60 seconds before next heartbeat/sweep
        await asyncio.sleep(60)


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_smart_sweeper())
