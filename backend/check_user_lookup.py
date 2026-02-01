import asyncio
from app.db.session import AsyncSessionLocal
import app.db.base # Register all models
from app.models.wallet import Wallet
from app.models.user import User
from sqlalchemy import select

async def check_user():
    address = "0x578FC7311a846997dc99bF2d4C651418DcFe309A"
    async with AsyncSessionLocal() as db:
        print(f"Checking for wallet: {address}")
        result = await db.execute(select(Wallet).where(Wallet.address == address))
        wallet = result.scalars().first()
        if wallet:
            print(f"Found Wallet! User ID: {wallet.user_id}")
            u_res = await db.execute(select(User).where(User.id == wallet.user_id))
            user = u_res.scalars().first()
            if user:
                print(f"Found User! Index: {user.derivation_index}")
            else:
                print("User NOT found for wallet.")
        else:
            print("Wallet NOT found.")

if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())
    asyncio.run(check_user())
