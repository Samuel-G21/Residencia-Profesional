import sys
import os
import io

sys.path.append(os.path.abspath('backend'))
from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    db.create_all()
    with app.test_client() as client:
        # We create a dummy Excel for 'extract-pdf' step or just upload dummy Excel to 'generate-docs'
        # To call generate-docs we need to upload an excel file
        import pandas as pd
        data = {
            'ID': ['123', '123'],
            'NOMBRE DEL EVENTO': ['Curso de Prueba', 'Curso de Prueba'],
            'DURACION': ['40', '40'],
            'INSTRUCTOR': ['Juan Perez', 'Juan Perez'],
            'FICHA INSTRUCTOR': ['12345', '12345'],
            'DIA I': ['01', '01'],
            'AÑO I': ['2023', '2023'],
            'DIA T': ['05', '05'],
            'AÑO T': ['2023', '2023'],
            'FICHA': ['001', '002'],
            'NOMBRE': ['Alex', 'Bob'],
            'PRIMER APELLIDO': ['Smith', 'Johnson'],
            'SEGUNDO APELLIDO': ['Doe', 'Williams'],
            'CATEGORIA': ['Cat1', 'Cat2'],
            'NIVEL': ['N1', 'N2'],
            'DEPARTAMENTO': ['Depto1', 'Depto2'],
        }
        df = pd.DataFrame(data)
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        response = client.post('/api/generate-docs', data={
            'file': (excel_file, 'asistencia.xlsx'),
            'id_evento': '123',
            'tipo_curso': 'Actualización',
            'docs_seleccionados': 'SIRCE_Automatizado.xlsm'
        })
        print(response.json)
