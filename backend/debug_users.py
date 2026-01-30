from app.db.base import Base # Ensure all models are loaded
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
import asyncio

async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"User: {u.email}, ID: {u.id}")

if __name__ == "__main__":
    asyncio.run(list_users())
