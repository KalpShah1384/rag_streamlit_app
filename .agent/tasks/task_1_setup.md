# Task 1: Project Environment & LLM Basics

**Goal:** Set up the development environment and perform a basic LLM call.

## Subtasks
1. [x] Initialize a new Git repository.
2. [x] Create a Python virtual environment (`python -m venv venv`).
3. [x] Create a `.env` file and add `OPENAI_API_KEY`.
4. [x] Create a `requirements.txt` file and install dependencies:
   ```
   langchain
   langchain-google-genai
   python-dotenv
   pypdf
   chromadb
   streamlit
   ```
5. [x] Create a `test_llm.py` script to verify the connection:
   - Load `.env`.
   - Initialize `ChatGoogleGenerativeAI`.
   - Call `.invoke("Hello, how are you?")`.

## Success Criteria
- [x] Dependencies are installed successfully.
- [x] `test_llm.py` runs and returns a valid response from the LLM.
