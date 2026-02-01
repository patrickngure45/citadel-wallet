from fastapi import APIRouter
from app.api.v1.endpoints import users, wallets, transactions, agreements, hearing, agent, market, protocol

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(agreements.router, prefix="/agreements", tags=["agreements"])
api_router.include_router(hearing.router, prefix="/hearing", tags=["hearing"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(protocol.router, prefix="/protocol", tags=["protocol"])


