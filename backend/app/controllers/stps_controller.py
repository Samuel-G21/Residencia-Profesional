from flask import request, jsonify, send_file
import os
import io
import copy
import openpyxl
from jinja2 import Template
from ..routes.stps import stps_bp
from ..models.course import Curso
from ..models.history import HistorialCapacitacion

@stps_bp.route('/evento/<id_evento>/stps/export', methods=['POST'])
def export_stps(id_evento):
    try:
        curso = Curso.query.filter_by(id_evento=id_evento).first()
        if not curso:
            return jsonify({"status": "error", "message": "Evento no encontrado."}), 404

        trabajadores = HistorialCapacitacion.query.filter_by(id_evento=id_evento).all()
        lista_participantes = []
        for t in trabajadores:
            if t.estado != 'BAJA':
                lista_participantes.append({
                    "ficha": t.ficha_trabajador,
                    "nombre_completo": t.nombre_trabajador,
                    "nombre_trabajador": t.nombre_trabajador,
                    "calificacion": t.calificacion if t.calificacion is not None else ""
                })

        data = {
            "clave_evento": id_evento,
            "id_evento": id_evento,
            "nombre_evento": curso.nombre_evento,
            "nombre_curso": curso.nombre_evento,
            "tipo_curso": curso.tipo_curso,
            "lista_participantes": lista_participantes
        }

        req_data = request.get_json(silent=True)
        if req_data:
            data.update(req_data)

        filepath = os.path.join('catalogos', 'STPS.xlsm')
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "No se ha subido el archivo base STPS.xlsm en catalogos."}), 404

        wb = openpyxl.load_workbook(filepath, keep_vba=True)
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str) and '{{' in cell.value:
                        try:
                            # Allow Jinja to render lista_participantes
                            cell.value = Template(cell.value).render(data)
                        except Exception as e:
                            print(f"Error procesando celda {cell.coordinate}: {e}")
        
        mem_file = io.BytesIO()
        wb.save(mem_file)
        
        # Guardar una copia en la carpeta de outputs
        evento_dir = os.path.join('outputs', str(id_evento).strip())
        os.makedirs(evento_dir, exist_ok=True)
        out_name = f'STPS_{id_evento}.xlsm'
        with open(os.path.join(evento_dir, out_name), 'wb') as f:
            f.write(mem_file.getvalue())

        mem_file.seek(0)
        
        return send_file(mem_file, mimetype='application/vnd.ms-excel.sheet.macroEnabled.12', as_attachment=True, download_name=f'STPS_{id_evento}.xlsm')

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@stps_bp.route('/evento/<id_evento>/scpm07/export', methods=['POST'])
def export_scpm07(id_evento):
    try:
        curso = Curso.query.filter_by(id_evento=id_evento).first()
        if not curso:
            return jsonify({"status": "error", "message": "Evento no encontrado."}), 404

        trabajadores = HistorialCapacitacion.query.filter_by(id_evento=id_evento).all()
        lista_participantes = []
        for t in trabajadores:
            if t.estado != 'BAJA':
                lista_participantes.append({
                    "ficha": t.ficha_trabajador,
                    "nombre_completo": t.nombre_trabajador,
                    "nombre_trabajador": t.nombre_trabajador,
                    "calificacion": t.calificacion if t.calificacion is not None else ""
                })

        data = {
            "clave_evento": id_evento,
            "id_evento": id_evento,
            "nombre_evento": curso.nombre_evento,
            "nombre_curso": curso.nombre_evento,
            "tipo_curso": curso.tipo_curso,
            "lista_participantes": lista_participantes
        }

        req_data = request.get_json(silent=True)
        if req_data:
            data.update(req_data)

        filepath = os.path.join('templates', 'SCPM-07.xlsx')
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "No se ha subido el archivo base SCPM-07.xlsx en templates."}), 404

        wb = openpyxl.load_workbook(filepath, keep_vba=False)
        for ws in wb.worksheets:
            start_row_idx = None
            end_row_idx = None
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        if '{% tr %}' in cell.value or '{% for participante in lista_participantes %}' in cell.value:
                            if start_row_idx is None:
                                start_row_idx = cell.row
                        if '{% endfor %}' in cell.value:
                            end_row_idx = cell.row
                if start_row_idx and end_row_idx:
                    break

            if start_row_idx and end_row_idx:
                block_size = end_row_idx - start_row_idx + 1
                num_participants = len(lista_participantes)
                
                if num_participants > 1:
                    ws.insert_rows(end_row_idx + 1, (num_participants - 1) * block_size)
                    for i in range(1, num_participants):
                        for r_offset in range(block_size):
                            src_row = start_row_idx + r_offset
                            tgt_row = start_row_idx + (i * block_size) + r_offset
                            for col_idx in range(1, ws.max_column + 1):
                                source = ws.cell(row=src_row, column=col_idx)
                                target = ws.cell(row=tgt_row, column=col_idx)
                                target.value = source.value
                                if source.has_style:
                                    target.font = copy.copy(source.font)
                                    target.border = copy.copy(source.border)
                                    target.fill = copy.copy(source.fill)
                                    target.number_format = source.number_format
                                    target.protection = copy.copy(source.protection)
                                    target.alignment = copy.copy(source.alignment)
                elif num_participants == 0:
                    ws.delete_rows(start_row_idx, block_size)

                if num_participants > 0:
                    for i, participante in enumerate(lista_participantes):
                        row_data = data.copy()
                        row_data['participante'] = participante
                        for r_offset in range(block_size):
                            tgt_row = start_row_idx + (i * block_size) + r_offset
                            for col_idx in range(1, ws.max_column + 1):
                                cell = ws.cell(row=tgt_row, column=col_idx)
                                if cell.value and isinstance(cell.value, str) and '{' in cell.value:
                                    val = cell.value.replace('{% tr %}', '')
                                    val = val.replace('paticipante.nombe_completo', 'participante.nombre_completo')
                                    val = val.replace('{% for participante in lista_participantes %}', '')
                                    val = val.replace('{% endfor %}', '')
                                    try:
                                        cell.value = Template(val).render(row_data)
                                    except Exception:
                                        pass

            for row in ws.iter_rows():
                # Skip the template block we just processed
                if start_row_idx and end_row_idx and start_row_idx <= row[0].row < start_row_idx + (len(lista_participantes) * block_size if len(lista_participantes) > 0 else 0):
                    continue
                for cell in row:
                    if cell.value and isinstance(cell.value, str) and '{' in cell.value:
                        try:
                            val = cell.value.replace('{% tr %}', '')
                            val = val.replace('{% for participante in lista_participantes %}', '')
                            val = val.replace('{% endfor %}', '')
                            cell.value = Template(val).render(data)
                        except Exception:
                            pass
        
        mem_file = io.BytesIO()
        wb.save(mem_file)
        mem_file.seek(0)
        
        return send_file(mem_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'SCPM-07_{id_evento}.xlsx')

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
