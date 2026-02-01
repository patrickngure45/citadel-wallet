
import asyncio
import os
from dotenv import load_dotenv

# Force load the .env from the root
load_dotenv(dotenv_path="../.env")

# Verify keys are loaded
import sys
# sys.path.append("..") # Ensure backend is in path
from app.services.llm_service import llm_service

async def test_llm():
    print("Testing LLM Service...")
    print(f"Groq Key Present: {bool(os.getenv('GROQ_API_KEY'))}")
    print(f"Gemini Key Present: {bool(os.getenv('GOOGLE_API_KEY'))}")
    
    intent = "Evacuate everything from Binance immediately"
    print(f"Running Debate for: {intent}")
    
    try:
        result = await llm_service.run_debate(intent)
        print("--- Result ---")
        print(result)
        if result:
            print("SUCCESS: Debate execution returned a result.")
        else:
            print("FAILURE: Debate execution returned None.")
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm())
