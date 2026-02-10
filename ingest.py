from core.loader import load_pdf
from core.splitter import split_documents
import os

def test_ingestion():
    sample_file = "artificial.pdf"
    
    if not os.path.exists(sample_file):
        print(f"❌ Error: {sample_file} not found.")
        return

    print(f"📖 Loading documents from {sample_file}...")
    docs = load_pdf(sample_file)
    print(f"✅ Loaded {len(docs)} document(s).")

    print(f"✂️ Splitting documents into chunks...")
    chunks = split_documents(docs, chunk_size=200, chunk_overlap=20)
    print(f"✅ Created {len(chunks)} chunks.")

    if chunks:
        print("\n📄 First Chunk Preview:")
        print("-" * 30)
        print(chunks[0].page_content)
        print("-" * 30)
        print(f"Character count: {len(chunks[0].page_content)}")

if __name__ == "__main__":
    test_ingestion()
