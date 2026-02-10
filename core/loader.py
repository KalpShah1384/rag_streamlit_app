from langchain_community.document_loaders import PyPDFLoader, TextLoader
from typing import List
from langchain_core.documents import Document

def load_pdf(file_path: str) -> List[Document]:
    """Loads a PDF file and returns a list of Documents."""
    loader = PyPDFLoader(file_path)
    return loader.load()

def load_txt(file_path: str) -> List[Document]:
    """Loads a text file and returns a list of Documents."""
    loader = TextLoader(file_path, encoding='utf-8')
    return loader.load()
