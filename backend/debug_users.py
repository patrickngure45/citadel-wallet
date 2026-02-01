from app.db.base import Base # Ensure all models are loaded
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
from app.services.wallet_service import wallet_service
import asyncio
import sys

async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"Total Users: {len(users)}")
        print(f"{'Email':<35} | {'Index':<5} | {'Address':<42}")
        print("-" * 90)
        
        for u in users:
            idx = u.derivation_index if u.derivation_index is not None else -1
            wallet = wallet_service.generate_evm_address(idx)
            addr = wallet["address"]
            print(f"{u.id} | {u.email:<35} | {idx:<5} | {addr}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(list_users())
