
import asyncio
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

async def test_google():
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"Key: {api_key[:5]}...")
    
    try:
        genai.configure(api_key=api_key)
        print("Listing models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
        
        # model = genai.GenerativeModel('gemini-1.5-flash')
        # print("Model initialized.")
        
        resp = await model.generate_content_async("Hello")
        print(f"Response: {resp.text}")
        print("✅ Google API Working")
    except Exception as e:
        print(f"❌ Google API Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_google())
