import pdfplumber

pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\03 50693527 SCPM01-100000.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            print(page.extract_text(x_tolerance=2, y_tolerance=2))
            print("--- TABLES ---")
            for tabla in page.extract_tables():
                for fila in tabla:
                    print(fila)
except Exception as e:
    print(f"Error: {e}")
