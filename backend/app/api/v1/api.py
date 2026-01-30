from fastapi import APIRouter
from app.api.v1.endpoints import users, wallets, transactions, agreements, hearing

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(agreements.router, prefix="/agreements", tags=["agreements"])
api_router.include_router(hearing.router, prefix="/hearing", tags=["hearing"])


