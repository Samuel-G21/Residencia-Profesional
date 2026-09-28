import os
import io
import pandas as pd
from flask import request

import sys
sys.path.append(os.path.abspath('backend'))
from app import create_app
from app.models import db
from app.controllers.document_controller import generate_docs

app = create_app()

with app.app_context():
    db.create_all()
    with app.test_request_context('/api/generate-docs', method='POST'):
        data = {
            'ID': ['123'],
            'NOMBRE DEL EVENTO': ['Curso Test'],
            'DURACION': ['10'],
            'INSTRUCTOR': ['Test Instructor'],
            'FICHA INSTRUCTOR': ['00000'],
            'FICHA': ['001'],
            'NOMBRE': ['Test'],
            'PRIMER APELLIDO': ['Worker'],
            'SEGUNDO APELLIDO': ['One'],
        }
        df = pd.DataFrame(data)
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        request.files = {'file': excel_file}
        request.form = {
            'id_evento': '123',
            'tipo_curso': 'Actualización',
            'docs_seleccionados': 'SCPM-05A.xlsx,SCPM-07.xlsx,SIRCE_Automatizado.xlsm',
            'modo_sirce': 'con_datos'
        }
        
        response = generate_docs()
        print(response[0].get_json())

    # Check if files were created
    outputs = os.listdir('outputs/123')
    print("Generated files:")
    for f in outputs:
        print(f)
