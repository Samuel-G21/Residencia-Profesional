import pdfplumber
import re
import sys

pdf_path = r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\03 50693527 SCPM01-100000.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        for page in pdf.pages: texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"

        txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))

        nombre_ev = None
        
        for p_idx, page in enumerate(pdf.pages):
            for t_idx, tabla in enumerate(page.extract_tables()):
                for r_idx, fila in enumerate(tabla):
                    for c_idx, celda in enumerate(fila):
                        if celda and isinstance(celda, str):
                            c_up = celda.upper().strip()
                            c_up_flat = c_up.replace('\n', ' ')
                            if c_up_flat.startswith('NOMBRE DEL EVENTO') or c_up_flat.startswith('NOMBRE DEL CURSO') or c_up_flat.startswith('NOMBRE DEL TALLER'):
                                print(f"Found match: '{c_up_flat}' at table {t_idx} row {r_idx} col {c_idx}")
                                if ':' in c_up_flat:
                                    val = c_up_flat.split(':', 1)[1].strip()
                                    if val: nombre_ev = val
                                elif '\n' in c_up:
                                    lines = c_up.split('\n')
                                    if lines[0].strip().startswith('NOMBRE DEL'):
                                        val = ' '.join(lines[1:]).strip()
                                        if val and val not in ('EVENTO', 'CURSO', 'TALLER', 'PROYECTO'):
                                            nombre_ev = val
                                
                                if not nombre_ev and c_idx + 1 < len(fila) and fila[c_idx + 1]:
                                    v = str(fila[c_idx+1]).replace('\n', ' ').strip()
                                    if v and not v.upper().startswith('FECHA') and v.upper() not in ('EVENTO', 'CURSO', 'TALLER', 'PROYECTO'):
                                        nombre_ev = v
                                if not nombre_ev and r_idx + 1 < len(tabla) and tabla[r_idx + 1][c_idx]:
                                    v = str(tabla[r_idx+1][c_idx]).replace('\n', ' ').strip()
                                    if v and v.upper() not in ('EVENTO', 'CURSO', 'TALLER', 'PROYECTO'):
                                        nombre_ev = v
                    if nombre_ev: break
                if nombre_ev: break
            if nombre_ev: break

        print(f"Name from table: {nombre_ev}")

        if not nombre_ev or nombre_ev in ('EVENTO', 'CURSO', 'TALLER', 'PROYECTO'):
            nombre_ev = None
            stop_words = r"\b(?:FECHA|DURACI[OÓ]N|OBJETIVO|PERIODO|MODALIDAD|HORARIO|SEDE|LUGAR|INSTRUCTOR|ID SIRHN|ALCANCE|PERFIL|DIRIGIDO|TIPO|PARTICIPANTES|CLAVE|NO\.|VIGENCIA)\b"
            nom_m = re.search(r"\b(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\b\s*[:\-]?\s*(.+?)(?=\s+" + stop_words + r"|$)", txt_flat)
            
            if not nom_m:
                nom_m = re.search(r"\b(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\b\s*[:\-]?\s*([^\n]{1,150})", texto_completo.upper())
            
            if nom_m:
                print(f"Name from regex: {nom_m.group(1).strip()}")
                val = nom_m.group(1).strip()
                if val.startswith("CURSO CC"): val = val.replace("CURSO CC", "").strip()
                if val: nombre_ev = val
        
        print(f"Final Name: {nombre_ev}")

except Exception as e:
    print(f"Error: {e}")
