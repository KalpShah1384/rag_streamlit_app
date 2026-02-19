import os
import time
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

def get_embeddings_model():
    """Returns the Google Generative AI embeddings model."""
    # Using the verified model name, leaving task_type to default for better query support
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

def create_vector_store(documents: List[Document], persist_directory: str = "faiss_db"):
    """
    Creates a FAISS vector store with robust batching and rate-limit handling.
    """
    embeddings = get_embeddings_model()
    
    # Process in small batches to respect Gemini Free Tier limits
    batch_size = 10 
    
    print(f"📦 Processing {len(documents)} chunks in batches of {batch_size}...")
    
    vector_store = None
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        print(f"⏳ Embedding batch {i//batch_size + 1}... ({min(i + batch_size, len(documents))}/{len(documents)})")
        
        success = False
        retries = 3
        while not success and retries > 0:
            try:
                if vector_store is None:
                    vector_store = FAISS.from_documents(batch, embeddings)
                else:
                    vector_store.add_documents(batch)
                success = True
            except Exception as e:
                # Catch rate limit / quota errors
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"⚠️ Quota hit. Waiting 30 seconds before retry... ({retries} retries left)")
                    time.sleep(30)
                    retries -= 1
                else:
                    raise e
        
        if not success:
            raise Exception("Failed to embed documents after multiple retries due to quota limits. Please try again in a few minutes.")

        # Brief delay between batches to stay under the burst limit
        time.sleep(3) 
    
    if vector_store:
        vector_store.save_local(persist_directory)
        print("✅ Vector Store Created & Saved Successfully!")
        return vector_store
    else:
        raise Exception("No documents found to process.")

def load_vector_store(persist_directory: str = "faiss_db"):
    """Loads an existing FAISS vector store from disk."""
    embeddings = get_embeddings_model()
    return FAISS.load_local(persist_directory, embeddings, allow_dangerous_deserialization=True)

def similarity_search(vector_store, query: str, k: int = 3):
    """Performs similarity search on the vector store."""
    return vector_store.similarity_search(query, k=k)
