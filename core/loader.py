from langchain_community.document_loaders import UnstructuredPDFLoader, UnstructuredAPIFileLoader, TextLoader
from typing import List
from langchain_core.documents import Document
import os

def load_pdf(file_path: str) -> List[Document]:
    """
    Loads a PDF with High-Res Images and Table support.
    Uses API on Cloud (to prevent crashes) and Local processing on PC.
    """
    api_key = os.getenv("UNSTRUCTURED_API_KEY")
    
    # Use API for Cloud (Prevents 1GB RAM Crash)
    if api_key:
        loader = UnstructuredAPIFileLoader(
            file_path=file_path,
            api_key=api_key,
            url="https://api.unstructuredapp.io/general/v1/general", 
            strategy="hi_res",
            extract_images_in_pdf=True,
            infer_table_structure=True,
            mode="elements" 
        )
    else:
        # Local processing (Fine for 16GB+ RAM PC, will crash on 1GB Cloud)
        loader = UnstructuredPDFLoader(
            file_path,
            strategy="hi_res",
            extract_images_in_pdf=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
        )
    
    return loader.load()

def load_txt(file_path: str) -> List[Document]:
    """Loads a text file and returns a list of Documents."""
    loader = TextLoader(file_path, encoding='utf-8')
    return loader.load()
