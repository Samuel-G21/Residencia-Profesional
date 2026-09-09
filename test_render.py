import os
from docxtpl import DocxTemplate

try:
    t_path = os.path.join('backend', 'templates', 'SCPM-05 2025.docx')
    doc = DocxTemplate(t_path)
    ctx_grp = {
        "clave_evento": "123",
        "nombre_evento": "Curso",
        "nombre_curso": "Curso",
        "duracion": "10",
        "nombre_instructor": "Inst",
        "ficha_instructor": "333",
        "fecha_inicio": "01/01/2025",
        "fecha_termino": "02/01/2025",
        "dia_inicio": "01",
        "mes_inicio": "01",
        "anio_inicio": "2025",
        "dia_termino": "02",
        "mes_termino": "01",
        "anio_termino": "2025",
        "lista_participantes": [{"ficha": "1", "nombre_completo": "A", "categoria": "B", "nivel": "C", "departamento": "D"}]
    }
    doc.render(ctx_grp)
    print("Renderizado exitoso")
except Exception as e:
    print(f"Error: {e}")
