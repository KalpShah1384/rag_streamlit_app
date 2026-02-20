# AI Knowledge Assistant PRO (Cloud Edition)

A high-performance RAG (Retrieval-Augmented Generation) system optimized for Streamlit Community Cloud, featuring Qdrant Cloud synchronization, Gemini-powered intelligence, and automated session management.

## 🌟 Key Features

- **Cloud Core**: Seamlessly migrates from local storage to **Qdrant Cloud** for persistent, scalable document indexing.
- **Smart Cleanup**: Automated session management that clears activity and temporary data after **1 hour** of inactivity to optimize space.
- **Cloud Optimized**: Specialized loading strategies (`auto`) and resource management to ensure stability on platforms with limited RAM (e.g., Streamlit Cloud 1GB limit).
- **Premium Intelligence**: Built on **Google Gemini 1.5 Flash** for rapid, accurate document analysis and table understanding.
- **Advanced UI**: sleek glassmorphism design with responsive sidebar and smooth animations.
- **Quota Resilience**: Robust error handling and exponential backoff retry logic for embedding API calls.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- Google Gemini API Key
- Qdrant Cloud Account (Free tier works perfectly)

### 2. Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_cloud_api_key
QDRANT_COLLECTION_NAME=knowledge_hub
```

### 3. Installation
```bash
pip install -r requirements.txt
```

### 4. Run Locally
```bash
streamlit run app.py
```

## ☁️ Deployment on Streamlit Cloud

1. Push your code to a GitHub repository.
2. In Streamlit Community Cloud:
   - Add the variables from `.env` to **Secrets**.
   - Ensure `packages.txt` is present (handled automatically in this repo).
   - Set the main file to `app.py`.

## 🛠️ Optimization Notes
- **Memory**: The app uses the `auto` strategy for PDF loading, which balances accuracy and memory. Image extraction is disabled by default for cloud stability.
- **Persistence**: unlike local storage, Qdrant Cloud ensures your documents are indexed once and accessible across sessions.
