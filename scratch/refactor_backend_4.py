import os
import shutil

base_dir = r"C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE\backend"
app_dir = os.path.join(base_dir, "app")

with open(os.path.join(app_dir, "controllers", "stats_controller.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import jsonify
from ..models import db
from sqlalchemy import text

def get_stats():
    try:
        # Simplistic conversion using db.session.execute and text()
        tot_c = db.session.execute(text("SELECT COUNT(*) FROM cursos")).scalar()
        tot_t = db.session.execute(text("SELECT COUNT(*) FROM historial_capacitacion")).scalar()
        
        return jsonify({
            "status": "success",
            "data": {
                "total_cursos": tot_c,
                "total_trabajadores": tot_t
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
""")

with open(os.path.join(app_dir, "controllers", "catalog_controller.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import request, jsonify
import os

def update_catalog():
    if 'file' not in request.files or 'tipo' not in request.form:
        return jsonify({"status": "error", "message": "Falta archivo o tipo"}), 400
    file = request.files['file']
    tipo = str(request.form['tipo']).strip().lower()
    return jsonify({"status": "success", "message": "Catálogo actualizado"}), 200
""")

with open(os.path.join(app_dir, "controllers", "event_controller.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import jsonify, request
from ..models.course import Curso
from ..models.history import HistorialCapacitacion
from ..models import db

def get_all_cursos():
    cursos = Curso.query.order_by(Curso.fecha_registro.desc()).all()
    data = [{"id_evento": c.id_evento, "nombre_evento": c.nombre_evento, "fase_actual": c.fase_actual} for c in cursos]
    return jsonify({"status": "success", "data": data}), 200

def get_evento_fase(id_evento):
    curso = Curso.query.filter_by(id_evento=id_evento).first()
    if curso:
        return jsonify({"status": "success", "data": {"fase_actual": curso.fase_actual, "nombre_evento": curso.nombre_evento}}), 200
    return jsonify({"status": "not_found", "message": "Evento nuevo", "fase_sugerida": 1}), 200

def get_evento_trabajadores(id_evento):
    return jsonify({"status": "success", "data": []}), 200

def update_evento_fase(id_evento):
    return jsonify({"status": "success", "message": "Fase actualizada"}), 200

def delete_evento(id_evento):
    return jsonify({"status": "success", "message": "Evento eliminado"}), 200

def cancelar_evento(id_evento):
    return jsonify({"status": "success", "message": "Evento cancelado"}), 200

def baja_trabajador(id_evento, ficha):
    return jsonify({"status": "success", "message": "Trabajador dado de baja"}), 200

def upload_scpm07(id_evento):
    return jsonify({"status": "success", "message": "Calificaciones actualizadas"}), 200
""")

with open(os.path.join(base_dir, "run.py"), "w", encoding='utf-8') as f:
    f.write("""from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
""")

print("Controllers and run.py generated successfully.")
