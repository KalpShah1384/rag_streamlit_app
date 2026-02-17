from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from typing import List
from langchain_core.documents import Document
import os
import pytesseract

# Handle Tesseract Path for Windows; Linux (Streamlit Cloud) should have it in PATH
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_PREFIX = r"C:\Program Files\Tesseract-OCR\tessdata"

if os.name == 'nt' and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX
else:
    # On Linux/Cloud, we rely on the system installation from packages.txt
    pass

def load_pdf(file_path: str) -> List[Document]:
    """
    Loads a PDF file optimized for Cloud/Mobile stability.
    Uses 'fast' strategy to prevent memory (OOM) crashes on 1GB RAM targets.
    """
    # Use 'fast' for better performance and lower RAM usage
    loader = UnstructuredPDFLoader(
        file_path,
        strategy="fast", 
    )
    return loader.load()

def load_txt(file_path: str) -> List[Document]:
    """Loads a text file and returns a list of Documents."""
    loader = TextLoader(file_path, encoding='utf-8')
    return loader.load()
