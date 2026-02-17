import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

def get_embeddings_model():
    """Returns the Google Generative AI embeddings model."""
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

def create_vector_store(documents: List[Document], persist_directory: str = "faiss_db"):
    """Creates a FAISS vector store from documents and persists it."""
    embeddings = get_embeddings_model()
    
    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )
    vector_store.save_local(persist_directory)
    return vector_store

def load_vector_store(persist_directory: str = "faiss_db"):
    """Loads an existing FAISS vector store from disk."""
    embeddings = get_embeddings_model()
    return FAISS.load_local(persist_directory, embeddings, allow_dangerous_deserialization=True)

def similarity_search(vector_store, query: str, k: int = 3):
    """Performs similarity search on the vector store."""
    return vector_store.similarity_search(query, k=k)
