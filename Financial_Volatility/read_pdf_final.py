import pdfplumber

try:
    with pdfplumber.open("/Users/karthikeyachalla/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/FCFAAA86-E7DF-4523-8383-D697834FD2F7/Project Report Template.pdf") as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        
    with open("pdf_text.txt", "w") as f:
        f.write(text)
    print("PDF text extracted.")
except Exception as e:
    print(f"Error: {e}")
