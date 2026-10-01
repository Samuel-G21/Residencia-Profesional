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
            if t.estado not in ('BAJA', 'NO APTO'):
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
                            ws.row_dimensions[cell.row].height = None
                            if cell.alignment:
                                new_align = copy.copy(cell.alignment)
                                new_align.wrap_text = True
                                new_align.shrink_to_fit = False
                                cell.alignment = new_align
                            else:
                                cell.alignment = openpyxl.styles.Alignment(wrap_text=True)
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
            if t.estado not in ('BAJA', 'NO APTO'):
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
        original_ws = wb.worksheets[0]
        
        original_title = original_ws.title
        
        chunk_size = 5
        participantes_chunks = [lista_participantes[i:i + chunk_size] for i in range(0, len(lista_participantes), chunk_size)]
        if not participantes_chunks:
            participantes_chunks = [[]]
            
        worksheets = []
        for chunk_idx in range(len(participantes_chunks)):
            ws = wb.copy_worksheet(original_ws)
            if len(participantes_chunks) > 1:
                ws.title = f"SCPM-07 ({chunk_idx + 1})"
            else:
                ws.title = original_title + " (new)"
            worksheets.append(ws)
            
        wb.remove(original_ws)
        if len(participantes_chunks) == 1:
            worksheets[0].title = original_title
            
        for chunk_idx, chunk in enumerate(participantes_chunks):
            ws = worksheets[chunk_idx]
                
            ficha_row = None
            nombre_row = None
            
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        if '{% for participante in lista_participantes %}' in cell.value or 'participante.ficha' in cell.value:
                            ficha_row = cell.row
                        if 'paticipante.nombe_completo' in cell.value or 'participante.nombre_completo' in cell.value:
                            nombre_row = cell.row
            
            if ficha_row and nombre_row:
                for col in range(9, 14):
                    ws.cell(row=ficha_row, column=col).value = ""
                    ws.cell(row=nombre_row, column=col).value = ""
                    
                for i, p in enumerate(chunk):
                    col = 9 + i
                    ws.cell(row=ficha_row, column=col).value = p.get('ficha', '')
                    ws.cell(row=nombre_row, column=col).value = p.get('nombre_completo', '')
                    
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str) and '{' in cell.value:
                        val = cell.value.replace('{% tr %}', '')
                        val = val.replace('paticipante.nombe_completo', 'participante.nombre_completo')
                        val = val.replace('{% for participante in lista_participantes %}', '')
                        val = val.replace('{% endfor %}', '')
                        try:
                            cell.value = Template(val).render(data)
                            ws.row_dimensions[cell.row].height = None
                            if cell.alignment:
                                new_align = copy.copy(cell.alignment)
                                new_align.wrap_text = True
                                new_align.shrink_to_fit = False
                                cell.alignment = new_align
                            else:
                                cell.alignment = openpyxl.styles.Alignment(wrap_text=True)
                        except Exception as e:
                            print(f"Template Error in cell {cell.coordinate}: '{cell.value}' - Error: {e}")
                            pass
        
        mem_file = io.BytesIO()
        wb.save(mem_file)
        mem_file.seek(0)
        
        return send_file(mem_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'SCPM-07_{id_evento}.xlsx')

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
