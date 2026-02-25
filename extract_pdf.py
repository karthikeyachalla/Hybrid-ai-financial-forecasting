"""
extract_pdf.py
Utility to extract text from a PDF file and print to stdout.
"""
import sys
import pdfplumber

def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python extract_pdf.py <pdf_path>')
        sys.exit(1)
    pdf_path = sys.argv[1]
    try:
        txt = extract_text(pdf_path)
        print(txt)
    except Exception as e:
        print(f'Error extracting PDF: {e}')
