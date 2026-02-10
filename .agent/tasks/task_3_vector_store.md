# Task 3: Vector Store & Embeddings

**Goal:** Store text chunks in a local vector database and perform similarity search.

## Subtasks
1. [x] Choose a vector database (FAISS chosen for Python 3.14 stability).
2. [x] Integrate `GoogleGenerativeAIEmbeddings`.
3. [x] Implement a `core/vector_store.py` module:
   - Function to create a new vector store from document chunks.
   - Function to load an existing vector store from disk (`save_local`/`load_local`).
   - Function to search for similar documents given a query string.
4. [x] Create a `test_search.py` script:
   - Ingest a sample document.
   - Run a query and assert that relevant chunks are retrieved.

## Success Criteria
- [x] Chunks are successfully embedded and stored.
- [x] Similarity search returns contextually relevant chunks.
- [x] Vector store persists across script restarts.
