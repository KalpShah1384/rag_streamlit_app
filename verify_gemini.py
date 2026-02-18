import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def check_model(name):
    print(f"--- Checking: {name} ---")
    try:
        llm = ChatGoogleGenerativeAI(model=name)
        res = llm.invoke("Hi")
        print(f"✅ Success: {res.content}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test common ones to find ANY that works
    check_model("gemini-2.5-flash")
    check_model("gemini-1.5-flash")
    check_model("gemini-2.0-flash-exp")
    check_model("gemini-pro")
