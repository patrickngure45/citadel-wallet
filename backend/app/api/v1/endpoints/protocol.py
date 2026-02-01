from typing import Any, Dict, List
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from app.services.wallet_service import wallet_service
from app.services.sweeper_service import sweeper_service
from app.core.config import settings

router = APIRouter()

# Global In-Memory State for MVP Autopilot Control
AUTOPILOT_STATE = {
    "enabled": False,
    "last_run": None,
    "status": "IDLE"
}

@router.get("/autopilot", response_model=Dict[str, Any])
def get_autopilot_status() -> Any:
    return AUTOPILOT_STATE

@router.post("/autopilot/toggle", response_model=Dict[str, Any])
def toggle_autopilot(enable: bool) -> Any:
    AUTOPILOT_STATE["enabled"] = enable
    AUTOPILOT_STATE["status"] = "RACING" if enable else "IDLE"
    return AUTOPILOT_STATE

@router.post("/autopilot/run")
async def run_autopilot_cycle(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """
    Manually trigger a single sweep cycle.
    Useful for testing or cron-job hooks.
    """
    if not AUTOPILOT_STATE["enabled"]:
        return {"status": "Ignored (Autopilot Disabled)"}
        
    background_tasks.add_task(sweeper_service.run_sweep_cycle)
    AUTOPILOT_STATE["last_run"] = str(datetime.now()) # crude timestamp
    return {"status": "Autopilot Cycle Initiated"}

@router.get("/stats", response_model=Dict[str, Any])
async def get_protocol_stats() -> Any:
    """
    Get Global Citadel Protocol Statistics.
    (Treasury Reserves, Escrow TVL, etc.)
    """
    chain = "bsc" if settings.NEXT_PUBLIC_USE_MAINNET else "bsc_testnet"
    
    # 1. Config Addresses
    TREASURY_ADDRESS = "0x571E52efc50055d760CEaE2446aE3B469a806279"
    TST_TOKEN = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
    
    # 2. Add Alice for monitoring
    ALICE_ADDRESS = "0x9E0b5FB77dAD5507360BdDdd2746F5B26A446390"
    
    # 3. Fetch Data
    try:
        # Treasury Holdings
        treasury_bnb = await wallet_service.get_balance(TREASURY_ADDRESS, chain)
        treasury_tst = wallet_service.get_token_balance(TREASURY_ADDRESS, TST_TOKEN, chain)
        
        # Test Pilot Stats
        alice_tst = wallet_service.get_token_balance(ALICE_ADDRESS, TST_TOKEN, chain)
        
        return {
            "network": "BSC Mainnet" if settings.NEXT_PUBLIC_USE_MAINNET else "BSC Testnet",
            "treasury": {
                "address": TREASURY_ADDRESS,
                "bnb": treasury_bnb,
                "tst": treasury_tst,
            },
            "pilots": {
                "alice_tst": alice_tst
            },
            "status": "Operational"
        }
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {
            "status": "Error",
            "error": str(e)
        }
