import subprocess
try:
    import pdfplumber
except ImportError:
    subprocess.check_call(["pip", "install", "pdfplumber"])
    import pdfplumber

text = ""
with pdfplumber.open("/Users/karthikeyachalla/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/FCFAAA86-E7DF-4523-8383-D697834FD2F7/Project Report Template.pdf") as pdf:
    for page in pdf.pages:
        text += page.extract_text() + "\n"
print(text)
