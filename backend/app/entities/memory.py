from app.entities.base import BaseEntity
from app.schemas.hearing import HearingRecord, MemoryOutput
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.wallet import Wallet
from sqlalchemy import select
import uuid

class MemoryEntity(BaseEntity):
    async def process(self, record: HearingRecord) -> HearingRecord:
        known_user = False
        derivation_index = None
        cex_config = {}
        
        try:
            async with AsyncSessionLocal() as db:
                user = None
                
                # 1. Try Lookup by UUID (User ID)
                try:
                    u_id = uuid.UUID(record.user_id)
                    result = await db.execute(select(User).where(User.id == u_id))
                    user = result.scalars().first()
                except ValueError:
                    # Not a UUID, proceed to address lookup
                    pass
                
                # 2. Try Lookup by Wallet Address
                if not user:
                    # Search for a wallet with this address
                    # distinct check to ensure we match generic string behavior
                    # Use ILIKE for case-insensitive address matching if supported, but standard select is safer
                    # We'll match lower() if needed, but for now exact string.
                    # Actually, usually stored Checksummed.
                    result = await db.execute(select(Wallet).where(Wallet.address == record.user_id))
                    wallet = result.scalars().first()
                    
                    if wallet:
                        # Fetch the owner
                        user_res = await db.execute(select(User).where(User.id == wallet.user_id))
                        user = user_res.scalars().first()

                if user:
                    known_user = True
                    derivation_index = user.derivation_index
                    cex_config = user.cex_config or {}
                    print(f"🧠 Memory: Recognized User {user.id} (Index {derivation_index})")
                else:
                    print(f"🧠 Memory: Unknown Subject {record.user_id}")

        except Exception as e:
            print(f"🧠 Memory Error: {e}")

        record.memory = MemoryOutput(
            known_user=known_user,
            derivation_index=derivation_index,
            relevant_precedents=[],
            anomalies=[],
            cex_config=cex_config
        )
        return record
