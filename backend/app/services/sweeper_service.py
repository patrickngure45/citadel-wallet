import asyncio
import uuid
from datetime import datetime
from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.models.hearing import HearingRecordModel
from app.models.user import User
from app.models.transaction import Transaction
from app.services.wallet_service import wallet_service
from app.core.config import settings
from app.entities.arena import Arena
from typing import List, Dict, Any

# CONFIGURATION
# The "Citadel" Cold Storage / Admin Hub
MASTER_WALLET_ADDRESS = "0x571E52efc50055d760CEaE2446aE3B469a806279"

# Determine Assets based on Environment
USE_MAINNET = settings.NEXT_PUBLIC_USE_MAINNET

ASSETS = []
if USE_MAINNET:
    ASSETS.append({
        "chain": "bsc",
        "symbol": "TST",
        "address": "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71",
        "min_sweep": 1.0
    })
else:
    ASSETS.append({
        "chain": "bsc_testnet",
        "symbol": "TST",
        "address": "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5",
        "min_sweep": 1.0
    })


async def fuel_user_wallet(user_address: str, amount_wei: int, chain: str) -> bool:
    """
    Sends native gas (BNB/MATIC) from the Deployer/Master wallet to the User wallet
    """
    print(f"  [GAS STATION] Pumping {amount_wei} wei to {user_address} on {chain}...")
    
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
        return False
        
    sender_account = w3.eth.account.from_key(settings.DEPLOYER_PRIVATE_KEY)
    sender_addr = sender_account.address
    
    # Buffer: Send 10% extra
    amount_to_send = int(amount_wei * 1.1)
    
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
    
    signed = w3.eth.account.sign_transaction(tx, settings.DEPLOYER_PRIVATE_KEY)
    try:
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"  [GAS SENT] Hash: {w3.to_hex(tx_hash)}")
        return True
    except Exception as e:
        print(f"Gas Pump Failed: {e}")
        return False

class SweeperService:
    def __init__(self):
        self.arena = Arena()
        
    async def run_sweep_cycle(self) -> List[str]:
        logs = []
        logs.append(f"Starting Sweep Cycle: {datetime.utcnow()}")
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            for user in users:
                user_data = wallet_service.generate_evm_address(user.derivation_index)
                user_addr = user_data["address"]
                
                for asset in ASSETS:
                    chain = asset["chain"]
                    symbol = asset["symbol"]
                    token_addr = asset["address"]
                    min_val = asset.get("min_sweep", 0)
                    
                    try:
                        # 1. Check Balance
                        balance = wallet_service.get_token_balance(user_addr, token_addr, chain)
                        
                        if balance < min_val:
                            continue
                            
                        logs.append(f"DETECTED {balance} {symbol} in {user_addr}")

                        # 2. Gas Check
                        GAS_LIMIT = 100000
                        if chain == "bsc_testnet":
                             w3 = wallet_service.w3_bsc_testnet
                        elif chain == "bsc":
                             w3 = wallet_service.w3_bsc
                        else:
                             continue

                        gas_price = w3.eth.gas_price
                        native_needed = GAS_LIMIT * gas_price
                        native_balance = w3.eth.get_balance(user_addr)
                        
                        if native_balance < native_needed:
                            amount_needed = native_needed - native_balance
                            success = await fuel_user_wallet(user_addr, amount_needed, chain)
                            if success:
                                logs.append(f"⛽ Pumped Gas to {user_addr}")
                                # Log to DB
                                gas_record = HearingRecordModel(
                                    id=uuid.uuid4(),
                                    user_id=user.id,
                                    intent=f"AUTOPILOT: Refuel Gas ({symbol})",
                                    started_at=datetime.utcnow(),
                                    transcript={"note": f"Pumped {amount_needed} wei"},
                                    final_verdict="EXECUTED",
                                    final_reason="Gas Required"
                                )
                                session.add(gas_record)
                                await session.commit()
                            else:
                                logs.append("❌ Gas Pump Failed")
                            
                            continue # Wait for next cycle for gas to arrive

                        # 3. Invoke Arena
                        intent_str = f"AUTOPILOT: Sweep all {symbol} to {MASTER_WALLET_ADDRESS}"
                        logs.append(f"Invoking Agent: {intent_str}")

                        record = await self.arena.conduct_hearing(
                            user_id=str(user.id),
                            intent=intent_str,
                            execute=True
                        )

                        logs.append(f"Agent Verdict: {record.final_verdict}")
                        
                        # 4. Save Record
                        # Since conduct_hearing doesn't save automatically sometimes? 
                        # Actually execution.py saves records? No, conduct_hearing returns a record, 
                        # usually the caller saves it if it's new.
                        # Wait, arena.conduct_hearing DOES NOT save to DB by default?
                        # Let's check Arena.conduct_hearing later. Typically it does NOT save.
                        
                        hearing_db = HearingRecordModel(
                            id=uuid.UUID(record.id),
                            user_id=user.id,
                            intent=record.intent,
                            started_at=record.started_at,
                            transcript=record.model_dump(mode='json'),
                            final_verdict=record.final_verdict,
                            final_reason=record.final_reason or "Autopilot Action"
                        )
                        session.add(hearing_db)
                        
                        if record.execution and record.execution.status == "SUCCESS":
                             logs.append(f"✅ Success: {record.execution.tx_hash}")
                             # Update Ledger
                             new_tx = Transaction(
                                user_id=user.id,
                                chain=chain,
                                symbol=symbol,
                                amount=balance,
                                type='DEPOSIT',
                                tx_hash=record.execution.tx_hash
                            )
                             session.add(new_tx)
                        
                        await session.commit()


                    except Exception as e:
                        logs.append(f"Error processing {symbol}: {str(e)}")
            
            # Heartbeat
            logs.append("Cycle Complete.")
            
        return logs

sweeper_service = SweeperService()
