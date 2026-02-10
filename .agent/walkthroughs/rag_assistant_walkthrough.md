# RAG Assistant Project Walkthrough

This walkthrough outlines the step-by-step process for building the AI Knowledge Assistant using LangChain and RAG.

## Phase 1: Foundations & Setup

### 1. Environment Configuration
- Ensure Python 3.10+ is installed.
- Create a virtual environment and initialize `.env`.
- Install core dependencies: `langchain`, `langchain-google-genai`, `chromadb`, `streamlit`.

### 2. Basic LLM Interaction
- Make a simple call to a Google Gemini model.
- Observe the impact of parameters like `temperature` and `max_tokens`.

## Phase 2: Document Processing Pipeline

### 3. Document Loading
- Implement `PyPDFLoader` for PDFs.
- Implement `TextLoader` for text files.

### 4. Text Chunking
- Use `RecursiveCharacterTextSplitter`.
- Set `chunk_size` (e.g., 1000) and `chunk_overlap` (e.g., 200).

## Phase 3: Embedding & Vector Storage

### 5. Generating Embeddings
- Use `GoogleGenerativeAIEmbeddings` to convert text chunks into vectors.

### 6. Vector Store Setup
- Initialize `Chroma` or `FAISS` to store embeddings locally.
- Implement persistence for the vector database.

## Phase 4: Retrieval & Generation (RAG)

### 7. Similarity Search
- Implement functions to search the vector store based on user queries.
- Adjust `k` to retrieve the most relevant chunks.

### 8. RAG Prompt Engineering
- Create a system prompt that forces the LLM to answer only using context.
- Handle cases where context is insufficient ("I don't know").

### 9. RAG Chain Construction
- Use `create_retrieval_chain` or custom `LangChain Expression Language (LCEL)` to link the retriever and the LLM.

## Phase 5: UI & UX

### 10. Streamlit Interface
- Add file uploaders for documents.
- Create a chat-like interface for querying.
- Display sources/citations for the generated answers.

## Phase 6: Advanced Features

### 11. Conversation Memory
- Use `ConversationBufferMemory` to maintain chat history.
- Ensure the model can handle follow-up questions.

### 12. Output Parsing
- Use `PydanticOutputParser` to get structured JSON responses when needed.

### 13. Agents & Tools
- (Optional) Enhance the assistant with the ability to search the web or filter specific metadata.
