import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.wallet import Wallet
from app.services.wallet_service import wallet_service
from app.core.config import settings
from sqlalchemy import select

# Configuration
MASTER_WALLET_ADDRESS = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce" # Your Hub

async def run_sweeper():
    print("="*50)
    print("CITADEL SWEEPER BOT ACTIVATED")
    print("="*50)
    print(f"Target Hub: {MASTER_WALLET_ADDRESS}")
    print("Scanning active user wallets for dust to sweep...")
    print("")

    async with AsyncSessionLocal() as session:
        # 1. Fetch all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"Checking {len(users)} users...")
        
        chains = ["bsc", "polygon"] # Add more as needed

        for user in users:
            print(f"User: {user.email} (Index {user.derivation_index})")
            
            for chain in chains:
                try:
                    # Attempt Sweep
                    result = await wallet_service.sweep_native(
                        from_index=user.derivation_index,
                        to_address=MASTER_WALLET_ADDRESS,
                        chain=chain
                    )
                    
                    if result and result.startswith("0x"):
                        print(f"  [SUCCESS] {chain.upper()}: Swept funds! TX: {result}")
                        # HERE: You would update database to say "User Deposited X" 
                        # technically you'd do that before sweeping, but for this simpler model
                        # the money is now in your pocket.
                    else:
                        print(f"  [SKIP]    {chain.upper()}: {result}")
                        
                except Exception as e:
                    print(f"  [ERROR]   {chain.upper()}: {e}")
            print("-" * 20)

if __name__ == "__main__":
    # Windows/Asyncio tweak
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(run_sweeper())
