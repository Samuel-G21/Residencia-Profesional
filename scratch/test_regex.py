import re

def test_extract(texto_completo):
    txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))
    stop_words = r"(?:FECHA|DURACI[OÓ]N|OBJETIVO|PERIODO|MODALIDAD|HORARIO|SEDE|LUGAR|INSTRUCTOR|ID SIRHN|ALCANCE|PERFIL|DIRIGIDO|TIPO|PARTICIPANTES|CLAVE|NO\.|VIGENCIA)"
    nom_m = re.search(r"(?:NOMBRE DEL (?:EVENTO|CURSO|TALLER|PROYECTO)|ACCI[OÓ]N DE CAPACITACI[OÓ]N|TEMA|CURSO)\s*[:\-]?\s*(.+?)(?=\s+" + stop_words + r"|$)", txt_flat)
    
    if nom_m:
        val = nom_m.group(1).strip()
        if val.startswith("CURSO CC"): val = val.replace("CURSO CC", "").strip()
        return val
    return "SIN DATO"

cases = [
    "ID SIRHN GENERADO 1234\nNOMBRE DEL EVENTO: CURSO CC 5CCAPCCX26 MANEJO SEGURO\nDE CLORO\nFECHA DE INICIO 12/03/2026",
    "TEMA\nSUPERVISION EFECTIVA\nEN PLANTA\nOBJETIVO GENERAL",
    "ACCIÓN DE CAPACITACIÓN\nTRABAJO EN ALTURAS\nLUGAR DEL EVENTO",
    "NOMBRE DEL PROYECTO: LIDERAZGO\nDURACIÓN 40 HRS",
    "CURSO\nCOMUNICACION\nASERTIVA\nPERFIL DEL PARTICIPANTE"
]

for c in cases:
    print(f"TEXT:\n{c}\nEXTRACTED: {test_extract(c)}\n")
