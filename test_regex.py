import pdfplumber
import re

pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\03 50693527 SCPM01-100000.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        for page in pdf.pages:
            texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"

        txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))
        
        stop_words = r"\b(?:FECHA|DURACI[OÓ]N|OBJETIVO|PERIODO|MODALIDAD|HORARIO|SEDE|LUGAR|INSTRUCTOR|ID SIRHN|ALCANCE|PERFIL|DIRIGIDO|TIPO|PARTICIPANTES|CLAVE|NO\.|VIGENCIA)\b"
        nom_m = re.search(r"\b(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\b\s*[:\-]?\s*(.+?)(?=\s+" + stop_words + r"|$)", txt_flat)
        
        if nom_m:
            print(f"REGEX 1 matched: {nom_m.group(1).strip()}")
        else:
            print("REGEX 1 no match")
            nom_m2 = re.search(r"\b(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\b\s*[:\-]?\s*([^\n]{1,150})", texto_completo.upper())
            if nom_m2:
                print(f"REGEX 2 matched: {nom_m2.group(1).strip()}")
            else:
                print("REGEX 2 no match")

except Exception as e:
    print(e)
