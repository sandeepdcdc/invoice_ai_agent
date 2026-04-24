import pytesseract
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open("invoice_sample.png")

text = pytesseract.image_to_string(img)

# Extract only required fields
invoice_match = re.search(r'Invoice\s*(No\.?|Number)?\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)

amount_match = re.search(
    r'Total\s*\(.*?\)\s*[:\-]?\s*\$?([\d,]+\.\d{2})',
    text,
    re.IGNORECASE
)

invoice_no = invoice_match.group(2) if invoice_match else "Not Found"
amount = amount_match.group(1) if amount_match else "Not Found"

# ✅ Only output required fields
print("Invoice No:", invoice_no)
print("Amount:", amount)