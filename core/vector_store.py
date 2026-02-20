import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "knowledge_base")

def get_embeddings_model():
    """Returns the Google Generative AI embeddings model."""
    api_key = os.getenv("GOOGLE_API_KEY")
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

def get_qdrant_client():
    """Initializes and returns a QdrantClient."""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=120.0,
        prefer_grpc=False
    )

def create_vector_store(documents: List[Document], persist_directory: str = None):
    """Creates a Qdrant collection using raw client to bypass Pydantic V1/Python 3.14 issues."""
    print("DEBUG: Starting create_vector_store (Raw Client Implementation)...")
    try:
        embeddings_model = get_embeddings_model()
        client = get_qdrant_client()
        
        # 1. Generate Embeddings first to determine dimension
        print(f"DEBUG: Embedding {len(documents)} documents to determine dimension...")
        texts = [doc.page_content for doc in documents]
        embeddings = embeddings_model.embed_documents(texts)
        
        if not embeddings:
            raise ValueError("No embeddings were generated.")
            
        vector_dim = len(embeddings[0])
        print(f"DEBUG: Detected vector dimension: {vector_dim}")
        
        # 2. Manage Collection
        collections = client.get_collections().collections
        if any(c.name == COLLECTION_NAME for c in collections):
            print(f"DEBUG: Deleting existing collection '{COLLECTION_NAME}'...")
            client.delete_collection(COLLECTION_NAME)
        
        print(f"DEBUG: Creating collection '{COLLECTION_NAME}' with dimension {vector_dim}...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=vector_dim, distance=models.Distance.COSINE),
        )
        
        # 3. Upload to Qdrant using raw client
        print("DEBUG: Uploading vectors to Qdrant Cloud...")
        points = []
        for i, (text, vector, doc) in enumerate(zip(texts, embeddings, documents)):
            payload = doc.metadata.copy()
            payload["page_content"] = text
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            ))
        
        # Batch upload
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print("DEBUG: Raw upload successful!")
        
        # Return a QdrantVectorStore instance for the app to use
        return QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings_model,
        )
    except Exception as e:
        import traceback
        print(f"DEBUG: Error in create_vector_store:\n{traceback.format_exc()}")
        raise e

def load_vector_store(persist_directory: str = None):
    """Loads an existing Qdrant vector store."""
    embeddings = get_embeddings_model()
    client = get_qdrant_client()
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

def similarity_search(vector_store, query: str, k: int = 3):
    """Performs similarity search."""
    return vector_store.similarity_search(query, k=k)
