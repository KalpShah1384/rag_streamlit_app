# Task 2: Document Ingestion Pipeline

**Goal:** Implement loaders and a chunking strategy for PDF and TXT files.

## Subtasks
1. [x] Create a `core/loader.py` module:
   - Implement `load_pdf(file_path)` using `PyPDFLoader`.
   - Implement `load_txt(file_path)` using `TextLoader`.
2. [x] Create a `core/splitter.py` module:
   - Configure `RecursiveCharacterTextSplitter`.
   - Set `chunk_size` = 1000, `chunk_overlap` = 200.
3. [x] Create an `ingest.py` script to test the pipeline:
   - Load a sample PDF/TXT.
   - Split it into chunks.
   - Print the character length of the first chunk and the total number of chunks.

## Success Criteria
- [x] Chunks are generated with the specified overlap.
- [x] Loader handles both PDF and TXT formats correctly.
