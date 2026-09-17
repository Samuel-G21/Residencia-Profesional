from flask import request, jsonify
import pandas as pd

def upload_excel():
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
        cursos_df = df[[col_id, col_nom]].drop_duplicates()
        cursos_lista = cursos_df.rename(columns={col_id: 'id', col_nom: 'nombre'}).to_dict('records')
        return jsonify({"status": "success", "data": cursos_lista}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
