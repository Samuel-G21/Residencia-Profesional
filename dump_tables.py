import pdfplumber
pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\03 50693527 SCPM01-100000.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for r in tables[0]:
                print(repr(r))
except Exception as e:
    print(e)
