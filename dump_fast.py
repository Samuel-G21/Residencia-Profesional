import pdfplumber
import re

pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\03 50693527 SCPM01-100000.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= 2:
                break
            print(f"--- PAGE {i} TEXT ---")
            print(page.extract_text(x_tolerance=2, y_tolerance=2))
            
            print(f"--- PAGE {i} TABLES ---")
            tables = page.extract_tables()
            for t_idx, tabla in enumerate(tables):
                for r_idx, fila in enumerate(tabla):
                    for c_idx, celda in enumerate(fila):
                        if celda and isinstance(celda, str) and 'SISTEMA' in celda.upper():
                            print(f"Table {t_idx} Row {r_idx} Col {c_idx}: {repr(celda)}")
                            
except Exception as e:
    print(e)
