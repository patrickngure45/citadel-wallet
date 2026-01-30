from app.services.wallet_service import wallet_service

# Configuration
TST_CONTRACT_ADDRESS = "0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71"
TST_CHAIN = "bsc"

# Debug / Phase 0 Bypass
# Since TST is currently untransferable due to contract issues, we allow 
# specific addresses to bypass the check for development purposes.
MOCK_BYPASS_ADDRESSES = [
    "0x578E5057088b9F65B20327f33A0360a0E06d5Da6", # External Test User
    "0x578FC7311a846997dc99bF2d4C651418DcFe309A", # Custodial User (Index 1)
]

class AccessControlService:
    """
    Manages user permissions based on their TST Token Holdings.
    This replaces the "sweep" logic with "gate" logic.
    """
    
    def check_access(self, user_address: str, required_amount: float) -> bool:
        """
        Synchronously checks if a user has enough TST.
        Returns True if Balance >= Required.
        """
        if user_address in MOCK_BYPASS_ADDRESSES:
            # print(f"[AccessControl] BYPASS ALLOWED for {user_address}")
            return True

        try:
            balance = wallet_service.get_token_balance(user_address, TST_CONTRACT_ADDRESS, TST_CHAIN)
            if balance >= required_amount:
                # In Phase 1, we might lock the tokens here.
                # For Phase 0, we just check.
                return True
            return False
        except Exception as e:
            print(f"[AccessControl] Error checking balance for {user_address}: {e}")
            return False

    async def get_user_tier(self, user_address: str) -> str:
        """
        Returns the user's tier based on TST holdings.
        """
        balance = wallet_service.get_token_balance(user_address, TST_CONTRACT_ADDRESS, TST_CHAIN)
        
        if balance >= 10000:
            return "INSTITUTIONAL"
        elif balance >= 1000:
            return "PROFESSIONAL"
        elif balance >= 100:
            return "STANDARD"
        else:
            return "OBSERVER"

access_control = AccessControlService()
