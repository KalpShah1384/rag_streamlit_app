import pytesseract
from pdf2image import convert_from_path
import os

def check_manual_install():
    print("🔍 Checking Tesseract and Poppler...")
    
    # Check Tesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract found! Version: {version}")
    except Exception as e:
        print(f"❌ Tesseract error: {str(e)}")
        print("Note: If you just updated the Path, you might need to restart your terminal/IDE.")

    # Check Poppler (by trying to convert first page of a PDF)
    test_pdf = "artificial.pdf"
    if os.path.exists(test_pdf):
        try:
            print(f"⏳ Testing Poppler on {test_pdf}...")
            images = convert_from_path(test_pdf, first_page=1, last_page=1)
            if images:
                print("✅ Poppler is working correctly!")
        except Exception as e:
            print(f"❌ Poppler error: {str(e)}")
    else:
        print(f"⚠️ {test_pdf} not found for Poppler test.")

if __name__ == "__main__":
    check_manual_install()
