from core.loader import load_pdf
from core.splitter import split_documents
from core.vector_store import create_vector_store, similarity_search
import os

def test_search():
    sample_file = "artificial.pdf"
    persist_dir = "faiss_db"
    
    if not os.path.exists(sample_file):
        print(f"❌ Error: {sample_file} not found.")
        return

    print("📖 Loading and splitting document (this may take a moment for a 20MB PDF)...")
    docs = load_pdf(sample_file)
    chunks = split_documents(docs, chunk_size=1000, chunk_overlap=100)
    
    print(f"💾 Creating vector store in '{persist_dir}'...")
    vector_store = create_vector_store(chunks, persist_directory=persist_dir)
    print("✅ Vector store created and persisted.")

    query = "What is the main topic of this document?"
    print(f"\n🔍 Searching for: '{query}'")
    results = similarity_search(vector_store, query, k=2)
    
    print(f"✅ Found {len(results)} relevant chunks:")
    for i, res in enumerate(results):
        print(f"\n--- Chunk {i+1} ---")
        print(res.page_content)
        print(f"Source: {res.metadata.get('source')}")

if __name__ == "__main__":
    test_search()
