# AI Knowledge Assistant Improvement Plan

## 1. Vector Database Migration (FAISS -> Qdrant Cloud)
- **Goal**: Move from local local storage (FAISS) to a managed cloud solution (Qdrant Cloud) for persistence and scalability.
- **Action**:
    - Update `core/vector_store.py` to use `langchain_qdrant`.
    - Securely load `QDRANT_URL` and `QDRANT_API_KEY` from `.env`.
    - Ensure collections are automatically created if they don't exist.

## 2. Session Management & Cleanup
- **Goal**: Prevent memory leaks and excessive storage usage by clearing sessions after 1 hour of inactivity.
- **Action**:
    - Implement a timestamp-based check in `app.py`.
    - Automatically reset `st.session_state` and clear temporary files if the session expires.

## 3. Multimodal Knowledge Extraction (Gemini Vision)
- **Goal**: Capture information from charts, graphs, and images that traditional OCR misses.
- **Action**:
    - Integrated `PyMuPDF` (fitz) for intelligent page scanning.
    - Added image-filtering logic (width > 300, height > 120) to focus on significant content.
    - Used Gemini 1.5 Flash to generate semantic descriptions of visual pages.
    - Descriptions are indexed as first-class documents in Qdrant, enabling "visual search".

## 4. Stability & Cloud Optimization (Streamlit Community Cloud Fix)

- **Goal**: Prevent crashes on Streamlit Cloud due to the 1GB RAM limit.
- **Action**:
    - **Document Loading**: Change `UnstructuredPDFLoader` strategy from `hi_res` to `auto` or `fast` to reduce memory consumption.
    - **Image Extraction**: Disable image extraction by default or optimize it.
    - **Resource Management**: Explicitly clear temporary uploads after processing.

## 4. Embedding & API Quota Management
- **Goal**: Gracefully handle "quota hit" errors from Google Gemini API.
- **Action**:
    - Enhance retry logic in `core/rag_chain.py` using `tenacity`.
    - Provide user-friendly error messages when quotas are reached, instead of crashing.

## 5. Security & User Experience Streamlining
- **Goal**: Simplify access by removing the login feature and polishing the UI.
- **Action**:
    - Remove `core/auth.py` integration from `app.py`.
    - Enhance the "Premium" CSS with improved animations and responsive design.
    - Implement a cleaner sidebar for document management.

## 6. Performance Improvements
- **Goal**: Faster response times and better retrieval.
- **Action**:
    - Implement BM25 hybrid search if possible with Qdrant.
    - Optimize chunk sizes for better context without hitting token limits.
