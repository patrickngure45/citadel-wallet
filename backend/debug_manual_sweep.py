import asyncio
import sys
from app.services.wallet_service import wallet_service
from app.core.config import settings

# Force Testnet for this check if needed, but the code handles it via settings
# We want to call sweep_native manually on User 0

TARGET_ADMIN = "0x571E86699318a6e84d4Cd151121d15A20662d5DE"

async def run_manual_sweep():
    print("--- Starting Manual Sweep Test ---")
    
    # We want to simulate what the Execution Entity does
    # The chain passed from LLM or Frontend might be "ETHEREUM" or "BSC_TESTNET"
    # But since we patched it, let's try calling it with "BSC_TESTNET" first
    # to confirm it works when the chain is correct.
    
    chain_to_use = "BSC_TESTNET" 
    
    print(f"Sweeping User 0 -> {TARGET_ADMIN} on {chain_to_use}")
    
    try:
        tx_hash = await wallet_service.sweep_native(
            from_index=0,
            to_address=TARGET_ADMIN,
            chain=chain_to_use
        )
        
        if tx_hash:
            print(f"SUCCESS! TX Hash: {tx_hash}")
        else:
            print("FAILURE: Returned None (Low Balance or Error)")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_manual_sweep())