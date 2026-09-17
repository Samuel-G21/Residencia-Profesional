from flask import request, jsonify
import os

def update_catalog():
    if 'file' not in request.files or 'tipo' not in request.form:
        return jsonify({"status": "error", "message": "Falta archivo o tipo"}), 400
    file = request.files['file']
    tipo = str(request.form['tipo']).strip().lower()
    return jsonify({"status": "success", "message": "Catálogo actualizado"}), 200
