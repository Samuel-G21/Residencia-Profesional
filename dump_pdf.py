import io
import pdfplumber
import re

pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\04 50693929 SCPM01-99224.pdf"

with pdfplumber.open(pdf_path) as pdf:
    texto_completo = ""
    for page in pdf.pages:
        texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"

    txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))
    
    val_m = re.search(r"ID SIRHN GENERADO\s*\d+\s+[A-ZÑ\s]+?F-?\d{5,6}\s+([A-ZÑ\s]+?)\s*F-?(\d{5,6})", txt_flat)
    if val_m:
        print("Supervisor match:", val_m.group(1).strip())
    else:
        print("Supervisor match: SIN DATO")

    inst_m = re.search(r"HORARIO.*?\d{2}:\d{2}.*?\s([A-ZÑ\s]+?)\s*F-?.*?(\d{5,6})", txt_flat)
    if inst_m:
        print("Instructor match:", inst_m.group(1).strip())
    else:
        print("Instructor match: SIN DATO")

