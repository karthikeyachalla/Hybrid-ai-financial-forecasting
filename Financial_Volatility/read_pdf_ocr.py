import subprocess
try:
    import pdf2image
    import pytesseract
except ImportError:
    subprocess.check_call(["pip", "install", "pdf2image", "pytesseract"])
    import pdf2image
    import pytesseract

from pdf2image import convert_from_path

try:
    images = convert_from_path("/Users/karthikeyachalla/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/FCFAAA86-E7DF-4523-8383-D697834FD2F7/Project Report Template.pdf")
    text = ""
    for i, image in enumerate(images):
        text += f"\n--- Page {i+1} ---\n"
        text += pytesseract.image_to_string(image)
    print(text[:2000])
    with open("extracted_template.txt", "w") as f:
        f.write(text)
except Exception as e:
    print("Failed to OCR:", e)

