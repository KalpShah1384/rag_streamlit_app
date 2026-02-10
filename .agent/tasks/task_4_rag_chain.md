# Task 4: Building the RAG Pipeline

**Goal:** Combine retrieval and generation to answer questions based on documents.

## Subtasks
1. [x] Define the RAG System Prompt:
   - "Use only the following context to answer the question. If you don't know, say 'I don't know'."
2. [x] Use LCEL (LangChain Expression Language) to build the chain:
   - `retriever` | `prompt` | `llm` | `StrOutputParser`.
3. [x] Implement sources metadata extraction:
   - Ensure the answer response includes which document or page the info came from.
4. [x] Create a `main.py` (CLI version):
   - Accepts a question, retrieves context, and prints the answer.

## Success Criteria
- [x] LLM answers questions using ONLY the provided context.
- [x] Hallucinations are minimized or eliminated for out-of-context queries.
- [x] Sources are correctly identified in the response.
