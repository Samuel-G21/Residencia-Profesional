import os
import sys
from io import BytesIO
from werkzeug.datastructures import FileStorage

sys.path.append(r"C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE")
from backend.app import create_app

app = create_app()

with app.test_request_context('/api/extract', method='POST'):
    with open(r"C:\Users\samy2\Downloads\OneDrive_1_15-9-2026\04 50693929 SCPM01-99224.pdf", 'rb') as f:
        file = FileStorage(stream=f, filename='04 50693929 SCPM01-99224.pdf', content_type='application/pdf')
        from backend.app.controllers.document_controller import extract_pdf
        from flask import request
        request.files = {'file': file}
        res = extract_pdf()
        
        with open('output_test.xlsx', 'wb') as out_f:
            out_f.write(res.data)

import pandas as pd
df = pd.read_excel('output_test.xlsx')
print(df[['NOMBRE SUPERVISOR', 'FICHA SUPERVISOR', 'NOMBRE INSTRUCTOR', 'FICHA INSTRUCTOR']])
