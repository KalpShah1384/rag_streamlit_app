import os
import io
import time
import uuid
import tempfile
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# Handle Tesseract Path for Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_PREFIX = r"C:\Program Files\Tesseract-OCR\tessdata"

if os.name == 'nt' and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
IMAGE_MODEL = "gemini/gemini-2.5-flash"
LLM_IMAGE_PROMPT = """Analyze this document page image. 
1. Describe any charts, graphs, or tables in detail.
2. If there are images or diagrams, explain what they represent.
3. If there is text that might be missed by standard OCR (stylized text, handwritten notes), transcribe it.
Return 'none' if the page contains no significant visual information besides plain text."""

def load_pdf(file_path: str) -> List[Document]:
    """
    Standard text extraction using Unstructured (fast strategy).
    We use 'fast' here because we handle images separately to save memory.
    """
    loader = UnstructuredPDFLoader(
        file_path,
        strategy="fast", # Use fast for text to save RAM
        extract_images_in_pdf=False,
        infer_table_structure=False,
        chunking_strategy="by_title",
    )
    return loader.load()

def process_pdf_images(file_path: str, filename: str) -> List[Document]:
    """
    User-requested logic: Process images in a PDF, generate descriptions via LLM.
    Returns a list of Documents containing the descriptions.
    """
    if not GEMINI_API_KEY:
        print("DEBUG: GOOGLE_API_KEY not found. Skipping image analysis.")
        return []

    doc = fitz.open(file_path)
    image_docs = []
    
    print(f"DEBUG: Processing PDF '{filename}' for visual content ({len(doc)} pages)...")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        
        has_large_image = False
        if image_list:
            for img in image_list:
                xref = img[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.width > 300 and pix.height > 120:
                        has_large_image = True
                        break
                    pix = None # Clear memory
                except Exception:
                    continue
        
        if has_large_image:
            print(f"DEBUG: Page {page_num+1}: Potential visual content detected. Analyzing...")
            
            # Render page as image for LLM
            page_pix = page.get_pixmap(dpi=200) # Lower DPI to save memory/upload time
            img_pil = Image.open(io.BytesIO(page_pix.tobytes("png")))
            
            # Convert to base64 for LiteLLM
            buffered = io.BytesIO()
            img_pil.save(buffered, format="PNG", optimize=True)
            import base64
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            description = None
            max_retries = 2
            for retry in range(max_retries):
                try:
                    llm_response = completion(
                        model=IMAGE_MODEL,
                        api_key=GEMINI_API_KEY,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": LLM_IMAGE_PROMPT},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                                ]
                            }
                        ]
                    )
                    description = llm_response['choices'][0]['message']['content']
                    break
                except Exception as e:
                    print(f"DEBUG: Page {page_num+1} analysis failed: {str(e)}")
                    time.sleep(2 ** (retry + 1))
            
            if description and description.strip().lower() != "none" and len(description) > 20:
                print(f"DEBUG: Page {page_num+1}: Description generated.")
                image_docs.append(Document(
                    page_content=f"[Visual Content Description for Page {page_num+1}]: {description}",
                    metadata={
                        "source": filename,
                        "page": page_num + 1,
                        "content_type": "image_description",
                        "dimensions": f"{img_pil.width}x{img_pil.height}"
                    }
                ))
            
            # Memory cleanup
            page_pix = None
            img_pil = None
            buffered = None

    doc.close()
    return image_docs

def load_txt(file_path: str) -> List[Document]:
    """Loads a text file."""
    loader = TextLoader(file_path, encoding='utf-8')
    return loader.load()
