import asyncio
import sys
import os
import uuid
import random
from sqlalchemy import select

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.agreement import Agreement, AgreementStatus

# Fix for "expression 'Wallet' failed to locate a name"
try:
    from app.models.wallet import Wallet
    from app.models.transaction import Transaction
    from app.models.hearing import HearingRecordModel
except ImportError:
    pass

async def execute_escrow_demo():
    print("\n🤝 STARTING ESCROW SIMULATION: 'The Citadel Handshake' 🤝")
    
    async with AsyncSessionLocal() as db:
        # 1. Get our Main Test User (The "Buyer" / Creator)
        res = await db.execute(select(User).filter(User.email == "test@citadel.com"))
        buyer = res.scalars().first()
        
        # Fallback to Admin User if test user fails
        if not buyer:
             res = await db.execute(select(User).filter(User.email == "azurefashion254@gmail.com"))
             buyer = res.scalars().first()
             
        if not buyer:
            print("❌ No valid user found for demo.")
            return

        print(f"User: {buyer.email} (ID: {buyer.id})")
        
        # 2. Create a "Pending" Agreement (Off-chain negotiation)
        # Represents: Buyer wants to pay 500 TST for "Consulting Services" to a vendor
        amount = 500.0
        vendor_email = f"vendor_{random.randint(1000, 9999)}@example.com"
        
        agreement = Agreement(
            id=uuid.uuid4(),
            creator_id=buyer.id,
            counterparty_email=vendor_email,
            chain="bsc_testnet",
            token_symbol="TST",
            amount=amount,
            status=AgreementStatus.PENDING,
            contract_address="OFF_CHAIN_NEGOTIATION"
        )
        db.add(agreement)
        await db.commit()
        print(f"\n[1] 📝 Drafted Agreement: Pay {amount} TST to {vendor_email}")
        
        # 3. "Lock" funds (Transition to ACTIVE)
        # In a real app, this waits for a blockchain TX. 
        # Here we simulate the On-Chain Event confirming the lock.
        await asyncio.sleep(2)
        print("\n[2] ⛓️  Detecting On-Chain Escrow Lock...")
        
        # User Sends funds to 0x922... (Mocked)
        tx_hash = f"0xescrow{uuid.uuid4().hex}"
        
        agreement.status = AgreementStatus.ACTIVE
        agreement.contract_address = "0x922bA3bD7866F92F0Caa2A544bb303A38922fb12"
        agreement.tx_hash = tx_hash
        
        await db.commit()
        print(f"     ✅ Funds Locked. Smart Contract Active.")
        print(f"     Hash: {tx_hash}")
        
        print("\n[3] 🚀 Dashboard Update Triggered.")
        print("     User can now see 'Active Agreement' in the Safe Zone.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(execute_escrow_demo())
