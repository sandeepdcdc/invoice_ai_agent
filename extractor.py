import pytesseract
from PIL import Image
import re
import io
from pdf2image import convert_from_bytes
from pdfminer.high_level import extract_text

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_invoice_data(file_bytes, filename):

    text = ""

    # ==============================
    # STEP 1: Extract text
    # ==============================
    if filename.lower().endswith(".pdf"):
        try:
            with open("temp.pdf", "wb") as f:
                f.write(file_bytes)

            text = extract_text("temp.pdf")

            if len(text.strip()) < 50:
                raise Exception("Low text")

        except:
            images = convert_from_bytes(file_bytes)
            for img in images:
                text += pytesseract.image_to_string(img)

    else:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)

    print("\n===== RAW TEXT =====\n")
    print(text)
    print("\n====================\n")

    # ==============================
    # STEP 2: Extract Invoice Number
    # ==============================
    invoice_no = "Not Found"

    # Pattern 1: Invoice # BPXINV-00550
    match1 = re.search(
        r'Invoice\s*#\s*([A-Z0-9\-]+)',
        text,
        re.IGNORECASE
    )

    # Pattern 2: Invoice Number / No
    match2 = re.search(
        r'Invoice\s*(Number|No\.?)\s*[:\-]?\s*([A-Z0-9\-]+)',
        text,
        re.IGNORECASE
    )

    if match1:
        invoice_no = match1.group(1)

    elif match2:
        invoice_no = match2.group(2)

    # Fallback
    if invoice_no == "Not Found":
        for line in text.split("\n"):
            if "invoice" in line.lower():
                match = re.search(r'([A-Z0-9\-]{5,})', line)
                if match:
                    invoice_no = match.group(1)
                    break

    # ==============================
    # STEP 3: Extract Amount
    # ==============================
    amount = "0.00"

    lines = text.split("\n")

    # Step 1: PRIORITY - exact keywords
    for line in lines:
       line_clean = line.strip()
       line_clean = re.sub(r'\s+', ' ', line_clean)

       if re.search(r'(total\s*due|grand\s*total|amount\s*due)', line_clean, re.IGNORECASE):
         match = re.search(r'([\d,]+\.\d{2})', line_clean)
         if match:
          amount = match.group(1)
          break


    # Step 2: fallback - ANY "Total" line (very important)
    if amount == "0.00":
      for line in lines:
        line_clean = line.strip()

        if re.search(r'\btotal\b', line_clean, re.IGNORECASE):
            match = re.search(r'([\d,]+\.\d{2})', line_clean)
            if match:
                amount = match.group(1)


    # Step 3: last fallback (pick LAST number in doc)
    if amount == "0.00":
        matches = re.findall(r'([\d,]+\.\d{2})', text)
        if matches:
           amount = matches[-1]


    # Cleanup
    amount = amount.replace(",", "")