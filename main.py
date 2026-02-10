import os
from core.rag_chain import get_rag_chain_with_sources
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    persist_dir = "faiss_db"
    if not os.path.exists(persist_dir):
        print(f"❌ Error: Vector store not found in '{persist_dir}'. Please run Task 3 first.")
        return

    print("🤖 AI Knowledge Assistant (RAG) is ready!")
    print("Type 'exit' to quit.")
    
    rag_chain = get_rag_chain_with_sources(persist_dir)

    while True:
        query = input("\n❓ Question: ")
        
        if query.lower() in ["exit", "quit"]:
            break
            
        if not query.strip():
            continue

        print("🧠 Thinking...")
        try:
            result = rag_chain(query)
            
            print("\n💡 Answer:")
            print("-" * 50)
            print(result["answer"])
            print("-" * 50)
            
            # Show unique sources
            sources = set(result["sources"])
            print(f"📚 Sources: {', '.join(sources)}")
            
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
