from flask import jsonify, request
from ..models.course import Curso
from ..models.history import HistorialCapacitacion
from ..models import db
from sqlalchemy import text
import pandas as pd

def get_all_cursos():
    sql = text("""
        SELECT c.id_evento, c.nombre_evento, c.fase_actual, c.fecha_registro, c.estado,
               COUNT(h.id) as total_participantes
        FROM cursos c
        LEFT JOIN historial_capacitacion h ON c.id_evento = h.id_evento
        GROUP BY c.id_evento, c.nombre_evento, c.fase_actual, c.fecha_registro, c.estado
        ORDER BY c.fecha_registro DESC
    """)
    result = db.session.execute(sql)
    data = []
    for row in result:
        data.append({
            "id_evento": row.id_evento,
            "nombre_evento": row.nombre_evento,
            "fase_actual": row.fase_actual,
            "fecha_registro": row.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if row.fecha_registro else None,
            "estado": row.estado,
            "total_participantes": row.total_participantes
        })
    return jsonify({"status": "success", "data": data}), 200

def get_evento_fase(id_evento):
    curso = Curso.query.filter_by(id_evento=id_evento).first()
    if curso:
        return jsonify({"status": "success", "data": {"fase_actual": curso.fase_actual, "nombre_evento": curso.nombre_evento, "estado": curso.estado, "id_evento": curso.id_evento}}), 200
    return jsonify({"status": "not_found", "message": "Evento nuevo", "fase_sugerida": 1}), 200

def get_evento_trabajadores(id_evento):
    sql = text("SELECT id, ficha_trabajador, nombre_trabajador, estado, calificacion FROM historial_capacitacion WHERE id_evento = :id")
    result = db.session.execute(sql, {"id": id_evento})
    data = []
    for row in result:
        data.append({
            "id": row.id,
            "ficha_trabajador": row.ficha_trabajador,
            "nombre_trabajador": row.nombre_trabajador,
            "estado": row.estado,
            "calificacion": float(row.calificacion) if row.calificacion is not None else None
        })
    return jsonify({"status": "success", "data": data}), 200

def update_evento_fase(id_evento):
    data = request.json
    nueva_fase = data.get('fase')
    if not nueva_fase:
        return jsonify({"status": "error", "message": "Falta la nueva fase"}), 400
    
    curso = Curso.query.filter_by(id_evento=id_evento).first()
    if curso:
        curso.fase_actual = nueva_fase
    else:
        curso = Curso(id_evento=id_evento, nombre_evento='Evento Manual', fase_actual=nueva_fase)
        db.session.add(curso)
    db.session.commit()
    return jsonify({"status": "success", "message": f"Fase actualizada a {nueva_fase}"}), 200

def delete_evento(id_evento):
    curso = Curso.query.filter_by(id_evento=id_evento).first()
    if curso:
        db.session.delete(curso)
        db.session.commit()
        return jsonify({"status": "success", "message": "Evento eliminado"}), 200
    return jsonify({"status": "error", "message": "Evento no encontrado"}), 404

def finalizar_evento(id_evento):
    curso = Curso.query.filter_by(id_evento=id_evento).first()
    if curso:
        curso.estado = 'FINALIZADO'
        db.session.commit()
        return jsonify({"status": "success", "message": "Evento finalizado"}), 200
    return jsonify({"status": "error", "message": "Evento no encontrado"}), 404

def cancelar_evento(id_evento):
    curso = Curso.query.filter_by(id_evento=id_evento).first()
    if curso:
        curso.estado = 'CANCELADO'
        db.session.commit()
        return jsonify({"status": "success", "message": "Evento cancelado"}), 200
    return jsonify({"status": "error", "message": "Evento no encontrado"}), 404

def baja_trabajador(id_evento, ficha):
    data = request.json or {}
    motivo = data.get('motivo', '')
    trabajador = HistorialCapacitacion.query.filter_by(id_evento=id_evento, ficha_trabajador=ficha).first()
    if trabajador:
        trabajador.estado = 'BAJA'
        trabajador.motivo_baja = motivo
        db.session.commit()
        return jsonify({"status": "success", "message": "Trabajador dado de baja"}), 200
    return jsonify({"status": "error", "message": "Trabajador no encontrado en el evento"}), 404

def upload_scpm07(id_evento):
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Falta el archivo SCPM-07"}), 400
    file = request.files['file']
    if not file.filename.endswith('.xlsx'):
        return jsonify({"status": "error", "message": "Debe ser un archivo Excel (.xlsx)"}), 400
    
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file, data_only=True)
        # Try complex template first
        if 'Propuesta' in wb.sheetnames:
            ws = wb['Propuesta']
            # Search for Ficha row and Promedio row
            ficha_row, calif_row = 30, 42  # default
            for r in range(25, 45):
                val = ws.cell(row=r, column=1).value
                if val and "Promedio final" in str(val):
                    calif_row = r
                    break
            
            for col in range(9, 30):
                ficha_val = ws.cell(row=ficha_row, column=col).value
                calif_val = ws.cell(row=calif_row, column=col).value
                if ficha_val and str(ficha_val).strip():
                    ficha_str = str(ficha_val).replace('.0', '').strip()
                    try:
                        calif = float(calif_val) if calif_val is not None else 0
                        trabajador = HistorialCapacitacion.query.filter_by(id_evento=id_evento, ficha_trabajador=ficha_str).first()
                        if trabajador:
                            trabajador.calificacion = calif
                    except ValueError:
                        continue
        else:
            # Fallback to flat pandas reading
            file.seek(0)
            df = pd.read_excel(file)
            df.columns = df.columns.astype(str).str.upper().str.strip()
            col_ficha = next((c for c in df.columns if 'FICHA' in c), None)
            col_calif = next((c for c in df.columns if 'CALIFICACI' in c), None)
            
            if not col_ficha or not col_calif:
                return jsonify({"status": "error", "message": "No se encontró el formato oficial ni las columnas de FICHA o CALIFICACION"}), 400
                
            for _, row in df.iterrows():
                ficha = str(row.get(col_ficha, '')).replace('.0', '').strip()
                calif_raw = row.get(col_calif, '')
                if not ficha or pd.isna(calif_raw) or str(calif_raw).strip() == '': continue
                try:
                    calif = float(calif_raw)
                    trabajador = HistorialCapacitacion.query.filter_by(id_evento=id_evento, ficha_trabajador=ficha).first()
                    if trabajador:
                        trabajador.calificacion = calif
                except ValueError:
                    continue
                    
        db.session.commit()
        return jsonify({"status": "success", "message": "Calificaciones actualizadas"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar el Excel: {str(e)}"}), 400
