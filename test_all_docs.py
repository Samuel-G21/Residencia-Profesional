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
        import pandas as pd
        data = {
            'ID': ['123'],
            'NOMBRE DEL EVENTO': ['Curso de Prueba'],
            'DURACION': ['40'],
            'INSTRUCTOR': ['Juan Perez'],
            'FICHA INSTRUCTOR': ['12345'],
            'DIA I': ['01'],
            'AÑO I': ['2023'],
            'DIA T': ['05'],
            'AÑO T': ['2023'],
            'FICHA': ['001'],
            'NOMBRE': ['Alex'],
            'PRIMER APELLIDO': ['Smith'],
            'SEGUNDO APELLIDO': ['Doe'],
            'CATEGORIA': ['Cat1'],
            'NIVEL': ['N1'],
            'DEPARTAMENTO': ['Depto1'],
        }
        df = pd.DataFrame(data)
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        
        # Test 1: Actualización, all templates
        excel_file.seek(0)
        response = client.post('/api/generate-docs', data={
            'file': (excel_file, 'asistencia.xlsx'),
            'id_evento': '123',
            'tipo_curso': 'Actualización',
            'docs_seleccionados': ''
        })
        print("Actualización (no docs specified):")
        print(response.json)
        
        # Test 2: Ascenso, all templates
        excel_file.seek(0)
        response = client.post('/api/generate-docs', data={
            'file': (excel_file, 'asistencia.xlsx'),
            'id_evento': '123',
            'tipo_curso': 'Ascenso',
            'docs_seleccionados': ''
        })
        print("\nAscenso (no docs specified):")
        print(response.json)
