import pdfplumber
import re
import sys
import glob

def test_pdfs():
    pdfs = glob.glob(r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\*.pdf")
    for pdf_path in pdfs:
        with pdfplumber.open(pdf_path) as pdf:
            texto_completo = ""
            for page in pdf.pages: texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"

            txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))

            # NEWEST REGEX
            inst_m = re.search(r"HORARIO.*?\d{2}:\d{2}[^\s]*\s+([A-ZÑ\s\.]+?)\s*(?:F-?)?\s*(?:(?:DES\.\s*)?EJECUTIVO)?\s*(?:F-?)?\s*(\d{5,6})", txt_flat)
            if inst_m:
                raw_inst = inst_m.group(1).strip()
                n_inst = re.sub(r'\b(?:DES\.\s*)?EJECUTIVO\b', '', raw_inst).strip()
                n_inst = re.sub(r'\s+', ' ', n_inst)
                f_inst = inst_m.group(2).strip()
            else:
                n_inst = "SIN DATO"
                f_inst = "SIN DATO"
            
            val_m = re.search(r"ID SIRHN GENERADO\s*\d+\s+[A-ZÑ\.\s]+?F-?\d{5,6}\s+([A-ZÑ\.\s]+?)\s*F-?(\d{5,6})", txt_flat)
            n_sup = val_m.group(1).strip() if val_m else "SIN DATO"
            f_sup = val_m.group(2).strip() if val_m else "SIN DATO"
            
            print(f"File: {pdf_path.split('\\')[-1]}")
            print(f"Instructor: {n_inst} Ficha: {f_inst}")
            print(f"Supervisor (Valida): {n_sup} Ficha: {f_sup}")

if __name__ == '__main__':
    test_pdfs()
