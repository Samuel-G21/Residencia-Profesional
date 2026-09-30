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
        
        inst3_m = re.search(r"HORARIO.*?\d{2}:\d{2}[^\s]*\s+([A-ZÑ\s\.]+?)\s*F-?.*?(\d{5,6})", txt_flat)
        if inst3_m:
            raw_inst = inst3_m.group(1).strip()
            clean_inst = re.sub(r'\bDES\.\s*EJECUTIVO\b', '', raw_inst).strip()
            clean_inst = re.sub(r'\s+', ' ', clean_inst)
        else:
            clean_inst = "SIN DATO"

        print(f"{pdf_file}: Instructor={clean_inst}")
