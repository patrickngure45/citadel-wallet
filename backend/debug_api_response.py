import asyncio
import httpx

async def check_api():
    async with httpx.AsyncClient() as client:
        # Mocking the request to the local server
        # Assuming port 8000
        try:
            response = await client.get("http://localhost:8000/api/v1/agent/summary")
            data = response.json()
            print("Status:", response.status_code)
            if "recent_actions" in data and len(data["recent_actions"]) > 0:
                print("Time Raw:", data["recent_actions"][0]["time"])
            else:
                print("No actions found")
        except Exception as e:
            print("Error connecting:", e)

if __name__ == "__main__":
    asyncio.run(check_api())
