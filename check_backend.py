import httpx
import asyncio

async def check_api():
    try:
        async with httpx.AsyncClient() as client:
            print("Checking API connection...")
            response = await client.get("http://127.0.0.1:8000/api/v1/market/yields?chain=BSC&token=USDT")
            print(f"Status: {response.status_code}")
            print(f"Data: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_api())