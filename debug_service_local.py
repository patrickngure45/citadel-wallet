import sys
import os
import asyncio
import time

# Fix path to include backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app.services.market_data_service import market_data
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def test_logic():
    print("Testing MarketDataService logic directly...")
    start = time.time()
    try:
        # Simulate what the API endpoint does
        data = await market_data.get_current_yields(chain="BSC", token="USDT")
        duration = time.time() - start
        
        print(f"Success! Duration: {duration:.2f}s")
        print(f"Result count: {len(data)}")
        for item in data:
            print(f" - {item}")
            
    except Exception as e:
        print(f"Logic Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_logic())