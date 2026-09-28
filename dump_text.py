import pdfplumber
import re

pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\03 50693527 SCPM01-100000.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        for page in pdf.pages:
            texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"

        txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))
        print("RAW TEXT:")
        print(txt_flat)

except Exception as e:
    print(e)
