import httpx
import asyncio

async def test_llama():
    base_url = "https://yields.llama.fi"
    try:
        print("Fetching pools...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/pools")
            print(f"Status: {response.status_code}")
            
            data = response.json()
            pools = data.get("data", [])
            print(f"Total Pools: {len(pools)}")
            
            # Inspect first pool to see structure
            if pools:
                print("Sample Pool Keys:", pools[0].keys())
                print("First Pool:", pools[0])
            
            # Test Filtering
            target_chain = "Binance" 
            token = "USDT"
            
            relevant_pools = []
            for p in pools:
                # Case insensitive check might be safer
                if p["chain"].lower() == "bsc" or p["chain"].lower() == "binance":
                    if p["symbol"].upper() == token:
                         relevant_pools.append(p)
            
            print(f"Found {len(relevant_pools)} relevant pools for {target_chain}/{token}")
            
            for p in relevant_pools[:5]:
                print(f"{p['project']} ({p['chain']}): {p['apy']}%")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llama())
