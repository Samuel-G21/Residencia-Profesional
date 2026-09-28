import pdfplumber
pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\03 50693527 SCPM01-100000.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for t_idx, tabla in enumerate(tables):
            for r_idx, fila in enumerate(tabla):
                for c_idx, celda in enumerate(fila):
                    if celda and isinstance(celda, str):
                        c_up = celda.upper().strip()
                        c_up_flat = c_up.replace('\n', ' ')
                        if c_up_flat.startswith('NOMBRE DEL EVENTO'):
                            print("FOUND IT:")
                            print("CELL:", repr(celda))
                            if c_idx + 1 < len(fila):
                                print("NEXT CELL:", repr(fila[c_idx+1]))
except Exception as e:
    print(e)
