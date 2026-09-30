tipo_curso = 'Actualización'
todas_ind = [
    '1. Cédula registro actualizado 2025 COMBIANADA.docx',
    'SCPM-05A.xlsx'
]
plantillas_ind = todas_ind.copy()

if tipo_curso.lower() != 'ascenso':
    plantillas_ind = [p for p in plantillas_ind if 'SCPM-05A' not in p]

print(plantillas_ind)
