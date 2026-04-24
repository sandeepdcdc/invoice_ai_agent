import pytesseract
from PIL import Image
import re
import io
from pdf2image import convert_from_bytes

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(file_bytes):
    images = convert_from_bytes(file_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text

def extract_invoice_data(file_bytes, filename):

    # Step 1: Extract text
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)

    # Step 2: Extract Invoice Number
    invoice_match = re.search(
        r'Invoice\s*(No\.?|Number)?\s*[:\-]?\s*(\d+)',
        text,
        re.IGNORECASE
    )

    # Step 3: Extract FINAL Total
    amount_match = re.search(
        r'(Total\s*\(.*?\)|Grand\s*Total|Amount\s*Due)[\s:₹]*\$?([\d,]+\.\d{2})',
        text,
        re.IGNORECASE
    )

    invoice_no = invoice_match.group(2) if invoice_match else "Not Found"
    amount = amount_match.group(2) if amount_match else "0"

    return invoice_no, amount