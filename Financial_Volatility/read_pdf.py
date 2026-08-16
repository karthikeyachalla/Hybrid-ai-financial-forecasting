import sys
try:
    import pypdf
except ImportError:
    import os
    os.system("pip install pypdf")
    import pypdf

reader = pypdf.PdfReader("/Users/karthikeyachalla/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/FCFAAA86-E7DF-4523-8383-D697834FD2F7/Project Report Template.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"
print(text)
