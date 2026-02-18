import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def test_models():
    models = ["gemini-1.5-flash", "gemini-pro", "models/gemini-1.5-flash"]
    for model_name in models:
        print(f"Testing model: {model_name}...")
        try:
            llm = ChatGoogleGenerativeAI(model=model_name)
            response = llm.invoke("Say hello")
            print(f"✅ Success with {model_name}: {response.content}")
            return model_name
        except Exception as e:
            print(f"❌ Failed with {model_name}: {str(e)}")
    return None

if __name__ == "__main__":
    test_models()
