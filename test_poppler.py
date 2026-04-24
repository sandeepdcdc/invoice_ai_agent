from pdf2image import convert_from_path

images = convert_from_path("invoice_test.pdf")

print("Pages:", len(images))