import requests
import json
import os
import sys

BASE_URL = 'http://localhost:5000/api'

def test():
    # 1. Create a dummy event by calling Phase 1 (generate-docs)
    id_evento = "999999"
    # Create a dummy data.xlsx
    import pandas as pd
    df = pd.DataFrame([
        {"ID": id_evento, "FICHA": "11111", "NOMBRE": "JUAN PEREZ", "DURACION HORAS": "10"}
    ])
    df.to_excel('test_data.xlsx', index=False)
    
    with open('test_data.xlsx', 'rb') as f:
        res = requests.post(f"{BASE_URL}/generate-docs", data={
            'id_evento': id_evento,
            'docs_seleccionados': 'SCPM-03.docx',
            'tipo_curso': 'Actualización'
        }, files={'file': f})
    
    print("Phase 1 response:", res.json())
    
    # 2. Add a new worker in Phase 2
    res = requests.post(f"{BASE_URL}/evento/{id_evento}/trabajador", json={
        "ficha": "22222",
        "nombre": "NUEVO TRABAJADOR"
    })
    print("Add worker response:", res.json())
    
    # 3. Generate Phase 2 docs
    res = requests.post(f"{BASE_URL}/generate-docs", data={
        'id_evento': id_evento,
        'docs_seleccionados': 'SCPM-04.docx',
        'tipo_curso': 'Actualización'
    })
    print("Phase 2 response:", res.json())
    
    # Check if doc for 22222 was generated
    docs_gen = res.json().get('data', [])
    found = any("22222" in doc for doc in docs_gen)
    print("Was NUEVO TRABAJADOR generated?", found)

if __name__ == "__main__":
    test()
