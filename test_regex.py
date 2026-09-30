import re

txt_flat = "SOLICITA VALIDA ID SIRHN GENERADO 50693929 ANUAR PAZ CRUZ F-327651 JUAN JOSE ESTRADA GODINEZ F-378258 RESPONSABLE DE LA SUPERINTENDENCIA DE FUERZA Y RESPONSABLE DE LA SUBGERENCIA DE ADMINISTRACION DE SERVICIOS PRINCIPALES LA PRODUCCION AREA USUARIA AREA USUARIA"

val_m = re.search(r"ID SIRHN GENERADO\s*\d+\s+([A-ZÑ\s]+?)F-?\d{5,6}\s+([A-ZÑ\s]+?)\s*F-?(\d{5,6})", txt_flat)
if val_m:
    print("Match 1:", val_m.group(1).strip())
    print("Match 2:", val_m.group(2).strip())
    print("Match 3:", val_m.group(3).strip())
else:
    print("No match")

val_m2 = re.search(r"ID SIRHN GENERADO\s*\d+\s+[A-ZÑ\s]+?F-?\d{5,6}\s+([A-ZÑ\s]+?)\s*F-?(\d{5,6})", txt_flat)
if val_m2:
    print("Original Match 1:", val_m2.group(1).strip())
    print("Original Match 2:", val_m2.group(2).strip())

