import pytesseract
from PIL import Image
import re
import io
from pdf2image import convert_from_bytes
from pdfminer.high_level import extract_text

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_invoice_data(file_bytes, filename):

    try:
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

        match1 = re.search(r'Invoice\s*#\s*([A-Z0-9\-]+)', text, re.IGNORECASE)
        match2 = re.search(r'Invoice\s*(Number|No\.?)\s*[:\-]?\s*([A-Z0-9\-]+)', text, re.IGNORECASE)

        if match1:
            invoice_no = match1.group(1)
        elif match2:
            invoice_no = match2.group(2)

        # fallback
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
        total_values = []

        # Step 1: PRIORITY keywords
        for line in lines:
            line_clean = line.strip()
            line_clean = re.sub(r'\s+', ' ', line_clean)

            if re.search(r'(total\s*due|grand\s*total|amount\s*due)', line_clean, re.IGNORECASE):
                match = re.search(r'([\d,]+\.\d{2})', line_clean)
                if match:
                    val = match.group(1).replace(",", "").replace("O", "0")
                    total_values.append(float(val))

        # Step 2: ALL "Total" lines
        for line in lines:
            line_clean = line.strip()

            if re.search(r'\btotal\b', line_clean, re.IGNORECASE):
                match = re.search(r'([\d,]+\.\d{2})', line_clean)
                if match:
                    val = match.group(1).replace(",", "").replace("O", "0")
                    total_values.append(float(val))

        # Step 3: fallback
        if not total_values:
         matches = re.findall(r'([\d,]+\.\d{2})', text)

        for m in matches:
          val = m.replace(",", "")
          val = val.replace("O", "0")
          total_values.append(float(val))

        # FINAL: pick max
        if total_values:
            amount = str(max(total_values))

        return invoice_no, amount

    except Exception as e:
        print("ERROR:", str(e))
        return "Not Found", "0.00"