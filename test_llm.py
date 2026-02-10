import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def test_connection():
    # Load environment variables from .env
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ Error: GOOGLE_API_KEY not found or not set in .env")
        return

    try:
        # Initialize ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        
        print("⏳ Sending test request to Google Gemini...")
        response = llm.invoke("Hello, how are you?")
        
        print("✅ Connection Successful!")
        print(f"🤖 Response: {response.content}")
        
    except Exception as e:
        print(f"❌ Connection Failed: {str(e)}")

if __name__ == "__main__":
    test_connection()
