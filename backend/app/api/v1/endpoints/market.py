from fastapi import APIRouter
from app.services.market_data_service import market_data

router = APIRouter()

@router.get("/yields")
async def get_yields(chain: str = "BSC", token: str = "USDT"):
    try:
        data = await market_data.get_current_yields(chain=chain, token=token)
        return data
    except Exception as e:
        return {"error": str(e)}
