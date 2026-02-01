import httpx
import asyncio
import time

class MarketDataService:
    def __init__(self):
        self.base_url = "https://yields.llama.fi"
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = 600  # 10 minutes cache

    async def _fetch_pools_with_cache(self):
        # Return cached data if valid
        if self._cache and (time.time() - self._cache_time < self._cache_ttl):
            return self._cache

        # Fetch new data with longer timeout
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{self.base_url}/pools")
            
        if response.status_code != 200:
            print(f"⚠️ DeFiLlama API Error: {response.status_code}")
            return []

        data = response.json()
        self._cache = data.get("data", [])
        self._cache_time = time.time()
        print(f"✅ Market Data Refreshed: {len(self._cache)} pools")
        return self._cache

    async def get_current_yields(self, chain: str = "BSC", token: str = "USDT"):
        """
        Fetches top yield opportunities from DeFiLlama for the given chain and token.
        """
        try:
            pools = await self._fetch_pools_with_cache()
            
            # If cache empty and fetch failed, fallback
            if not pools:
                return self._get_fallback_yields()
            
            # Filter for specific chain and token
            # chain mapped: 'BSC' in DeFiLlama for Binance Smart Chain
            target_chain = "BSC" if chain in ["BSC", "BSC_TESTNET"] else "Ethereum"
            
            relevant_pools = []
            seen_protocols = set()

            for p in pools:
                # Case-insensitive chain match just in case, and symbol match
                if p["chain"].upper() == target_chain and p["symbol"].upper() == token and p["tvlUsd"] > 1000000: # Min $1M TVL
                     
                     # Format Name: "lista-lending" -> "Lista Lending"
                     raw_name = p["project"]
                     if raw_name in seen_protocols:
                         continue # Skip duplicates (keep the first/best one found since we sort later usually, or we can sort first)
                     
                     display_name = raw_name.replace("-", " ").title().replace("V3", "v3").replace("Dao", "DAO")
                     
                     relevant_pools.append({
                         "protocol": display_name,
                         "apy": p["apy"],
                         "tvl": p["tvlUsd"],
                         "risk": "Low" if p["apy"] < 8 else ("Medium" if p["apy"] < 20 else "High")
                     })
                     seen_protocols.add(raw_name)
            
            # Sort by APY descending
            relevant_pools.sort(key=lambda x: x["apy"], reverse=True)
            
            # Return top 3 + Citadel (Manual Boost)
            top_3 = relevant_pools[:3]
            
            # If empty (API mismatch), fallback
            if not top_3:
                return self._get_fallback_yields()

            formatted_options = []
            for pool in top_3:
                formatted_options.append({
                    "protocol": pool["protocol"],
                    "apy": f"{pool['apy']:.2f}%",
                    "risk": pool["risk"]
                })
            
            # Add Citadel's "Proprietary" Vault (The 'Hook')
            # In a real app, this would be your own smart contract strategy
            formatted_options.append({
                "protocol": "Citadel Auto-Compounder", 
                "apy": "12.50%", 
                "risk": "Optimized"
            })
            
            return formatted_options

        except Exception as e:
            print(f"⚠️ Market Data Error: {e}")
            return self._get_fallback_yields()

    def _get_fallback_yields(self):
        return [
            {"protocol": "Aave V3 (Fallback)", "apy": "4.50%", "risk": "Low"},
            {"protocol": "Venus (Fallback)", "apy": "5.20%", "risk": "Medium"},
            {"protocol": "Citadel Vault", "apy": "12.50%", "risk": "Optimized"}
        ]

market_data = MarketDataService()
