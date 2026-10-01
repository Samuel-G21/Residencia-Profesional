import sys
import io
import pandas as pd
from werkzeug.datastructures import FileStorage

sys.path.append(r"C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE")
from backend.app import create_app
from backend.app.models import db
from backend.app.models.course import Curso
from backend.app.models.history import HistorialCapacitacion

app = create_app()

with app.app_context():
    # 1. Simulate Phase 1: create event and data.xlsx
    id_evento = '999998'
    with app.test_request_context('/api/generate-docs', method='POST'):
        df = pd.DataFrame([{'ID': id_evento, 'FICHA': '11111', 'NOMBRE': 'JUAN PEREZ', 'DURACION HORAS': '10'}])
        import os
        os.makedirs(f'outputs/{id_evento}', exist_ok=True)
        df.to_excel(f'outputs/{id_evento}/data.xlsx', index=False)
        from backend.app.controllers.document_controller import generate_docs
        from flask import request
        request.form = {'id_evento': id_evento, 'docs_seleccionados': 'SCPM-03.docx', 'tipo_curso': 'Actualización'}
        request.files = {}
        res1 = generate_docs()
        print('Phase 1:', res1[0].json)
    
    # 2. Add new worker manually
    with app.test_request_context(f'/api/evento/{id_evento}/trabajador', method='POST', json={'ficha': '22222', 'nombre': 'NUEVO TRABAJADOR'}):
        from backend.app.controllers.event_controller import agregar_trabajador
        res2 = agregar_trabajador(id_evento)
        print('Add worker:', res2[0].json)

    # 3. Generate Phase 2
    with app.test_request_context('/api/generate-docs', method='POST'):
        request.form = {'id_evento': id_evento, 'docs_seleccionados': 'SCPM-04.docx', 'tipo_curso': 'Actualización'}
        request.files = {}
        res3 = generate_docs()
        print('Phase 2:', res3[0].json)

    # 4. Check outputs dir
    print("Files in outputs:", os.listdir(f'outputs/{id_evento}'))
