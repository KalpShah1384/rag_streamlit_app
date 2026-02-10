import os
from core.rag_chain import get_rag_chain_with_sources
from dotenv import load_dotenv

def test_rag_integration():
    load_dotenv()
    
    persist_dir = "faiss_db"
    if not os.path.exists(persist_dir):
        print(f"❌ Error: Vector store not found.")
        return

    print("🧪 Testing RAG Pipeline Integration...")
    rag_chain = get_rag_chain_with_sources(persist_dir)

    test_query = "What is the role of AI and ML in the energy section according to the document?"
    print(f"❓ Query: {test_query}")
    
    result = rag_chain(test_query)
    
    print("\n💡 Answer:")
    print(result["answer"])
    
    print(f"\n📚 Sources found: {set(result['sources'])}")
    
    if len(result["answer"]) > 50:
        print("\n✅ Task 4 Verification Successful!")

if __name__ == "__main__":
    test_rag_integration()
