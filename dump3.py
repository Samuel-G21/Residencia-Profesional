import pdfplumber
pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\04 50694147 SCPM01-95840.pdf"
with pdfplumber.open(pdf_path) as pdf:
    print(pdf.pages[0].extract_text(x_tolerance=2, y_tolerance=2))
