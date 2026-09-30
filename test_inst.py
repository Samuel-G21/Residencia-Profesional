import io
import pdfplumber
import re
import os

pdf_dir = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026"
pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

for pdf_file in pdfs:
    pdf_path = os.path.join(pdf_dir, pdf_file)
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        for page in pdf.pages:
            texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"

        txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))
        
        # Original regex
        inst_m = re.search(r"HORARIO.*?\d{2}:\d{2}.*?\s([A-ZÑ\s]+?)\s*F-?.*?(\d{5,6})", txt_flat)
        inst1 = inst_m.group(1).strip() if inst_m else "SIN DATO"

        # Try to find the INSTRUCTOR/PROVEEDOR label instead
        inst2_m = re.search(r"INSTRUCTOR/PROVEEDOR:\s*([A-ZÑ\s\.]+?)\s*F-?(\d{5,6})", txt_flat)
        inst2 = inst2_m.group(1).strip() if inst2_m else "SIN DATO"
        
        # Alternatively, HORARIO followed by names that might have dots
        inst3_m = re.search(r"HORARIO.*?\d{2}:\d{2}[^\s]*\s+([A-ZÑ\s\.]+?)\s*F-?.*?(\d{5,6})", txt_flat)
        inst3 = inst3_m.group(1).strip() if inst3_m else "SIN DATO"

        print(f"{pdf_file}:\n  Orig={inst1}\n  New1={inst2}\n  New2={inst3}")
