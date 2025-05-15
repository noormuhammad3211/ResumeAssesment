import pdfplumber
from io import BytesIO

def extract_cv_text(file):
    with pdfplumber.open(BytesIO(file.read())) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text
