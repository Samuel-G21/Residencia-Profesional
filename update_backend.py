import re

with open('backend/app/controllers/document_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("'SCPM-05A.xls'", "'SCPM-05A.xlsx'")
content = content.replace("'SCPM-03.docx',\n            'SIRCE_Automatizado.xlsm'\n", "'SCPM-03.docx'\n")
content = content.replace("'SCPM-03.docx',\r\n            'SIRCE_Automatizado.xlsm'\r\n", "'SCPM-03.docx'\r\n")

old_regex = r\"\"\"            if not nombre_ev:
                nom_m = re.search(r\"NOMBRE DEL (?:EVENTO|CURSO|TALLER)\s*[:\-]?\s*(.{1,150}?)\s+(?:FECHA|DURACI[OÓ]N|OBJETIVO|PERIODO|MODALIDAD|HORARIO|SEDE|LUGAR|INSTRUCTOR|ID SIRHN|ALCANCE|PERFIL|DIRIGIDO|TIPO|PARTICIPANTES|CLAVE|NO\.)\", txt_flat)
                if not nom_m:
                    nom_m = re.search(r\"NOMBRE DEL (?:EVENTO|CURSO|TALLER)\s*[:\-]?\s*([^\n]{1,150})\", texto_completo.upper())\"\"\"

new_regex = r\"\"\"            if not nombre_ev:
                nom_m = re.search(r\"(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\s*[:\-]?\s*(.{1,200}?)\s+(?:FECHA|DURACI[OÓ]N|OBJETIVO|PERIODO|MODALIDAD|HORARIO|SEDE|LUGAR|INSTRUCTOR|ID SIRHN|ALCANCE|PERFIL|DIRIGIDO|TIPO|PARTICIPANTES|CLAVE|NO\.)\", txt_flat)
                if not nom_m:
                    lines = [l.strip() for l in texto_completo.upper().split('\\n') if l.strip()]
                    for i, l in enumerate(lines):
                        if re.match(r'^(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)[:\-]?$', l):
                            if i + 1 < len(lines):
                                nombre_ev = lines[i+1].strip()
                                break
                    if not nombre_ev:
                        nom_m = re.search(r\"(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\s*[:\-]?\s*([^\n]{1,150})\", texto_completo.upper())\"\"\"

if old_regex in content:
    content = content.replace(old_regex, new_regex)
else:
    print('Failed to find old regex block')

with open('backend/app/controllers/document_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated document_controller.py')
