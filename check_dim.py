import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def check_dim():
    api_key = os.getenv("GOOGLE_API_KEY")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )
    vector = embeddings.embed_query("test")
    print(f"DIM_RESULT:{len(vector)}")

if __name__ == "__main__":
    check_dim()
