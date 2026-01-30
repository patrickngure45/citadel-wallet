from typing import List, Union
import os
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Explicitly load dotenv
load_dotenv()
# Also try loading from specific locations if CWD fails
load_dotenv("backend/.env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Citadel Protocol"
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    # Changed to List[str] to allow "*" or other patterns without strict URL validation
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except ValueError:
                return v.split(",")
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/citadel"

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Union[str, None]) -> Any:
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Security
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SECURE_SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Wallet / Master Key
    # Added default for initial deployment safety
    CITADEL_MASTER_SEED: str = "deployment-placeholder-seed-change-in-prod"

    # RPC Nodes (Defaults to public/free tiers for dev)
    ETHEREUM_RPC_URL: str = "https://eth.llamarpc.com"
    BSC_RPC_URL: str = "https://binance.llamarpc.com"
    POLYGON_RPC_URL: str = "https://polygon.llamarpc.com"
    
    # Optional deployer key for gas pumping
    DEPLOYER_PRIVATE_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",  
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
