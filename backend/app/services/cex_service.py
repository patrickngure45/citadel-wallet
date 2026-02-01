import httpx
import time
import hmac
import hashlib
import urllib.parse
from typing import Dict, List, Any

class CexService:
    """
    The 'Hands' that reach into Centralized Exchanges (Binance).
    Uses lightweight HTTP requests (no heavy ccxt dependency).
    """
    def __init__(self):
        self.base_url = "https://api.binance.com"
        

    def _sign_params(self, params: Dict[str, Any], secret: str) -> str:
        """
        Signs the parameters using HMAC SHA256 as required by Binance.
        """
        # Sort params 
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def get_market_price(self, symbol: str) -> float:
        """
        Get public market price for risk calc.
        """
        # MOCK FOR TST PROTOCOL
        if "TST" in symbol:
            return 1.337
            
        try:
            # Ensure correct format for Binance API (ETHUSDT not ETH/USDT)
            clean_symbol = symbol.replace("/", "").upper()
            if "USDT" not in clean_symbol:
                 clean_symbol += "USDT"
                 
            async with httpx.AsyncClient() as client:
                 # No key needed for public price
                 res = await client.get(f"https://api.binance.com/api/v3/ticker/price?symbol={clean_symbol}")
                 data = res.json()
                 return float(data['price'])
        except Exception as e:
            # Fallback for demo
            import random
            if "ETH" in symbol: return 2500.0 * random.uniform(0.99, 1.01)
            return 0.0

    async def get_user_balance(self, exchange_id: str, api_key: str, api_secret: str) -> Dict[str, float]:
        """
        Connects to a user's private CEX account to read holdings.
        """
        # MOCK SIMULATION MODE
        if api_key == "MOCK_KEY" or api_key == "SIMULATION" or not api_secret:
             return {"ETH": 1.5, "USDT": 2500.0, "BNB": 10.0}

        # ONLY SUPPORT BINANCE FOR NOW
        if exchange_id.lower() != "binance":
             return {"BTC": 0.5, "USDT": 100.0}

        endpoint = "/api/v3/account"
        
        # 1. Prepare Parameters
        timestamp = int(time.time() * 1000)
        params = {
            "timestamp": timestamp,
            "recvWindow": 5000
        }
        
        # 2. Sign
        signature = self._sign_params(params, api_secret)
        params["signature"] = signature
        
        headers = {
            "X-MBX-APIKEY": api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}", 
                    params=params, 
                    headers=headers
                )
                
            if response.status_code != 200:
                print(f"⚠️ Binance API Error: {response.text}")
                return {}

            data = response.json()
            balances = data.get("balances", [])
            
            # 3. Filter & Format
            holdings = {}
            for b in balances:
                free = float(b.get("free", 0))
                if free > 0.00000001:
                    holdings[b["asset"]] = free
            
            return holdings

        except Exception as e:
            print(f"⚠️ CexService Error: {e}")
            return {}

    async def withdraw_to_chain(self, exchange_id: str, api_key: str, api_secret: str, token: str, amount: float, address: str, chain: str) -> str:
        """
        Withdraws funds from CEX to the User's On-Chain Wallet.
        WARNING: MOVES REAL FUNDS.
        """
        # 0. Safety Check
        if api_key == "SIMULATION" or api_key == "MOCK_KEY":
            import random
            print(f"🌊 SIMULATION: Withdrawing {amount} {token} to {address}")
            return f"tx_evac_{random.randint(100000, 999999)}_{token.lower()}"

        print(f"🚨 EXECUTING REAL WITHDRAWAL: {amount} {token} -> {address}")
        
        # 1. Map Network
        network = "ETH" # Default
        if "BSC" in chain or "BINANCE" in chain: network = "BSC"
        elif "POLYGON" in chain or "MATIC" in chain: network = "MATIC"
        elif "TRON" in chain: network = "TRX"
        elif "SOLANA" in chain: network = "SOL"
        
        # 2. Prepare Request
        endpoint = "/sapi/v1/capital/withdraw/apply"
        timestamp = int(time.time() * 1000)
        
        params = {
            "coin": token,
            "address": address,
            "amount": amount,
            "network": network,
            "timestamp": timestamp,
            "recvWindow": 10000
        }
        
        # 3. Sign
        signature = self._sign_params(params, api_secret)
        params["signature"] = signature
        
        headers = { "X-MBX-APIKEY": api_key }
        
        # 4. Execute
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(f"{self.base_url}{endpoint}", params=params, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                # Binance returns {"id": "string_uuid"}
                return data.get("id")
            else:
                err_msg = res.text
                print(f"❌ Binance Withdraw Error: {err_msg}")
                # Fallback Exception for flow control
                raise Exception(f"Binance Withdrawal Failed: {err_msg}")
    
    async def close(self):
        pass

cex_service = CexService()
