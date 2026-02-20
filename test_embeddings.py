import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def test():
    try:
        print("Initializing Embeddings model...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )
        print("Testing single embedding...")
        vector = embeddings.embed_query("Hello world")
        print(f"Success! Vector length: {len(vector)}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
