import sys

file_path = "backend/app/controllers/document_controller.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = '''            if not nombre_ev:
                nom_m = re.search(r"(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\\s*[:\\-]?\\s*(.{1,200}?)\\s+(?:FECHA|DURACI[OÓ]N|OBJETIVO|PERIODO|MODALIDAD|HORARIO|SEDE|LUGAR|INSTRUCTOR|ID SIRHN|ALCANCE|PERFIL|DIRIGIDO|TIPO|PARTICIPANTES|CLAVE|NO\\.)", txt_flat)
                if not nom_m:
                    lines = [l.strip() for l in texto_completo.upper().split('\\n') if l.strip()]
                    for i, l in enumerate(lines):
                        if re.match(r'^(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)[:\\-]?$', l):
                            if i + 1 < len(lines):
                                nombre_ev = lines[i+1].strip()
                                break
                    if not nombre_ev:
                        nom_m = re.search(r"(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\\s*[:\\-]?\\s*([^\\n]{1,150})", texto_completo.upper())
                if nom_m and not nombre_ev:
                    val = nom_m.group(1).strip()
                    if val.startswith("CURSO CC"): val = val.replace("CURSO CC", "").strip()
                    if val: nombre_ev = val'''

replacement = '''            if not nombre_ev:
                stop_words = r"(?:FECHA|DURACI[OÓ]N|OBJETIVO|PERIODO|MODALIDAD|HORARIO|SEDE|LUGAR|INSTRUCTOR|ID SIRHN|ALCANCE|PERFIL|DIRIGIDO|TIPO|PARTICIPANTES|CLAVE|NO\\.|VIGENCIA)"
                nom_m = re.search(r"(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\\s*[:\\-]?\\s*(.+?)(?=\\s+" + stop_words + r"|$)", txt_flat)
                
                if not nom_m:
                    nom_m = re.search(r"(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\\s*[:\\-]?\\s*([^\\n]{1,150})", texto_completo.upper())
                
                if nom_m:
                    val = nom_m.group(1).strip()
                    if val.startswith("CURSO CC"): val = val.replace("CURSO CC", "").strip()
                    if val: nombre_ev = val'''

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Success: File updated.")
else:
    print("Error: Target content not found.")
