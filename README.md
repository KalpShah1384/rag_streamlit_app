# AI Knowledge Assistant (LangChain + RAG)

A document-aware intelligence system built with LangChain and RAG (Retrieval-Augmented Generation). This assistant can ingest documents (PDF, TXT), understand user queries, retrieve relevant information, and generate accurate, grounded answers.

## 🚀 Key Features

- **Document Ingestion**: Seamlessly load and process PDF and TXT files.
- **RAG Pipeline**: Advanced retrieval logic ensuring grounded and hallucination-free answers.
- **Conversation Memory**: Remembers context for follow-up questions.
- **Modern UI**: Clean and interactive interface built with Streamlit.
- **Structured Output**: Support for JSON and Pydantic parsers for reliable data extraction.

## 🛠️ Technology Stack

- **Framework**: LangChain
- **LLM**: Google Gemini (1.5 Flash/Pro)
- **Vector Store**: ChromaDB / FAISS
- **Frontend**: Streamlit
- **Environment**: Python 3.10+

## 📋 Execution Plan Overview

The project is divided into several phases:
1.  **Foundations & Setup**: Environment configuration.
2.  **LLM & Prompt Fundamentals**: Understanding model behavior.
3.  **LangChain Core**: Mastering the building blocks.
4.  **Document Pipeline**: Loading and chunking.
5.  **Embeddings & Vector Store**: Storage and retrieval.
6.  **RAG Core Logic**: Connecting everything.
7.  **Conversation Memory**: Adding context awareness.
8.  **Output & Safety**: Reliability and error handling.
9.  **Advanced Tooling**: Agents and custom tools.
10. **UI Development**: Streamlit integration.
11. **Optimization**: Cost and performance.
12. **Deployment**: Finalizing for production.

## ⚙️ Setup Instructions

1.  **Install Python 3.10+**
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install langchain langchain-community langchain-google-genai faiss-cpu chromadb streamlit pypdf python-dotenv
    ```
4.  **Configure API Keys**:
    Create a `.env` file and add your `GOOGLE_API_KEY`.

## 📖 Walkthrough

For a detailed step-by-step guide, please refer to the [.agent/walkthroughs/rag_assistant_walkthrough.md](.agent/walkthroughs/rag_assistant_walkthrough.md).
