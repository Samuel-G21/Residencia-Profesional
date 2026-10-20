"""
Controlador auxiliar para inspeccion de cursos dentro de archivos Excel (`excel_controller.py`).

Guia para practicantes:
Permite subir un archivo `.xlsx` de asistencia y extraer la lista de eventos unicos
identificados por las columnas `ID` y `NOMBRE DEL EVENTO`.
"""
from flask import request, jsonify
from ..utils.security import error_response
import pandas as pd


def upload_excel():
    """
    Endpoint `POST /api/upload-excel`.
    Lee un archivo Excel y devuelve un arreglo JSON con `{id, nombre}` por cada curso distinto.
    """
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Sin archivo"}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.xlsx'):
        return jsonify({"status": "error", "message": "Formato inválido (.xlsx)"}), 400

    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.upper().str.strip()
        col_id = 'ID'
        col_nom = 'NOMBRE DEL EVENTO'
        if col_id not in df.columns or col_nom not in df.columns:
            return jsonify({"status": "error", "message": "Falta ID o NOMBRE DEL EVENTO"}), 400

        # Filtra combinaciones unicas de ID y nombre de evento
        cursos_df = df[[col_id, col_nom]].drop_duplicates()
        cursos_lista = cursos_df.rename(columns={col_id: 'id', col_nom: 'nombre'}).to_dict('records')
        return jsonify({"status": "success", "data": cursos_lista}), 200
    except Exception as e:
        return error_response("Ocurrió un error interno", 500, e)
