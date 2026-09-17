from flask import request, jsonify, send_file
import os
import io
import re
import zipfile
import requests
import pandas as pd
import pdfplumber
from datetime import datetime
from docxtpl import DocxTemplate
from pypdf import PdfWriter
from ..models.course import Curso
from ..models.history import HistorialCapacitacion
from ..models import db

def safe_str(val):
    if pd.isna(val) or val == '': return ""
    try:
        f_val = float(val)
        if f_val.is_integer(): return str(int(f_val))
        return str(val).strip()
    except:
        return str(val).strip()

def generate_docs():
    if 'file' not in request.files or 'id_evento' not in request.form:
        return jsonify({"status": "error", "message": "Faltan datos"}), 400

    file = request.files['file']
    id_evento = str(request.form['id_evento']).strip()

    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.upper().str.strip()
        df = df.fillna('')
        if 'ID' not in df.columns: return jsonify({"status": "error", "message": "Falta columna ID"}), 400
        df['ID'] = df['ID'].astype(str)
        trabajadores_curso = df[df['ID'] == id_evento]

        if trabajadores_curso.empty: return jsonify({"status": "error", "message": "Sin trabajadores"}), 404

        diccionario_curps = {}
        ruta_curp = os.path.join('catalogos', 'CURP.xlsx')
        if os.path.exists(ruta_curp):
            try:
                df_curp = pd.read_excel(ruta_curp)
                df_curp.columns = df_curp.columns.str.upper().str.strip()
                if 'FICHA' in df_curp.columns and 'CURP' in df_curp.columns:
                    for _, r_curp in df_curp.iterrows():
                        diccionario_curps[safe_str(r_curp['FICHA'])] = str(r_curp['CURP']).upper()
            except Exception as e:
                print("Error leyendo CURP.xlsx:", e)

        row0 = trabajadores_curso.iloc[0]
        nombre_curso = str(row0.get('NOMBRE DEL EVENTO', '')).strip().upper()
        duracion_curso = str(row0.get('DURACION HORAS', row0.get('DURACION', ''))).strip()
        tipo_curso = request.form.get('tipo_curso', 'Actualización')

        nombre_instructor = str(row0.get('INSTRUCTOR', row0.get('NOMBRE INSTRUCTOR', ''))).strip().title()
        ficha_instructor = str(row0.get('FICHA INSTRUCTOR', '')).strip()

        dia_i = safe_str(row0.get('DIA I', '')).zfill(2)
        mes_i = safe_str(row0.get('MES I', '')).zfill(2)
        anio_i = safe_str(row0.get('AÑO I', '')).split('.')[0]
        dia_t = safe_str(row0.get('DIA T', '')).zfill(2)
        mes_t = safe_str(row0.get('MES T', '')).zfill(2)
        anio_t = safe_str(row0.get('AÑO T', '')).split('.')[0]

        f_inicio = f"{dia_i}/{mes_i}/{anio_i}" if anio_i else ""
        f_termino = f"{dia_t}/{mes_t}/{anio_t}" if anio_t else ""

        docs_seleccionados_str = request.form.get('docs_seleccionados')
        
        todas_ind = [
            '1. Cédula registro actualizado 2025 COMBIANADA.docx',
            '2. Constancias de Habilidades DC-3 2026 COMBINADA.docx',
            'SCPM-04 COMBINADA.docx',
            'SCPM-04.docx',
            'SCPM-06 COMBINADA.docx'
        ]
        
        todas_grp = [
            '5. Carta Compromiso Instructor 2026 COMBINADA.docx',
            'FVC.docx',
            'Informe Técnico Instructor 2025.docx',
            'SCPM-05 2025.docx'
        ]

        todas_grp.append('SCPM-07.xlsx')

        if docs_seleccionados_str:
            lista_seleccionados = [d.strip() for d in docs_seleccionados_str.split(',')]
            plantillas_ind = [p for p in todas_ind if p in lista_seleccionados]
            plantillas_grp = [p for p in todas_grp if p in lista_seleccionados]
        else:
            plantillas_ind = todas_ind
            plantillas_grp = todas_grp

        evento_dir = os.path.join('outputs', id_evento)
        os.makedirs(evento_dir, exist_ok=True)
        for f in os.listdir(evento_dir):
            os.remove(os.path.join(evento_dir, f))

        docs_gen = []
        historial = []
        lista_participantes = []

        for _, row in trabajadores_curso.iterrows():
            ficha = safe_str(row.get('FICHA', ''))
            nombres = str(row.get('NOMBRE', row.get('NOMBRE(S)', ''))).strip().title()
            pat = str(row.get('PRIMER APELLIDO', '')).strip().title()
            mat = str(row.get('SEGUNDO APELLIDO', '')).strip().title()
            nombre_completo = f"{pat} {mat} {nombres}".strip()
            cat = str(row.get('CATEGORIA', row.get('CATEGORÍA', ''))).strip()
            niv = str(row.get('NIVEL', '')).strip()
            depto = str(row.get('DEPARTAMENTO', '')).strip()
            curp = diccionario_curps.get(ficha, "SIN CURP EN CATALOGO")

            if ficha:
                lista_participantes.append({
                    "ficha": ficha,
                    "nombre_completo": nombre_completo,
                    "categoria": cat,
                    "nivel": niv,
                    "departamento": depto
                })
                historial.append({
                    "id_evento": id_evento, 
                    "ficha_trabajador": ficha, 
                    "nombre_trabajador": nombre_completo
                })

            ctx_ind = {
                "ficha": ficha,
                "ficha_trabajador": ficha,
                "apellido_paterno": pat,
                "apellido_materno": mat,
                "nombre": nombres,
                "nombres": nombres,
                "nombre_completo": nombre_completo,
                "nombre_trabajador": nombre_completo,
                "curp": curp,
                "CURP": curp,
                "nombre_evento": nombre_curso,
                "nombre_curso": nombre_curso,
                "clave_evento": id_evento,
                "duracion": duracion_curso,
                "nombre_instructor": nombre_instructor,
                "ficha_instructor": ficha_instructor,
                "fecha_inicio": f_inicio,
                "fecha_termino": f_termino,
                "dia_inicio": dia_i,
                "mes_inicio": mes_i,
                "anio_inicio": anio_i,
                "dia_termino": dia_t,
                "mes_termino": mes_t,
                "anio_termino": anio_t,
                "categoria": cat,
                "categoria_trabajador": cat,
                "nivel": niv,
                "departamento": depto,
                "tipo_curso": tipo_curso
            }

            for p in plantillas_ind:
                t_path = os.path.join('templates', p)
                if os.path.exists(t_path):
                    try:
                        doc = DocxTemplate(t_path)
                        doc.render(ctx_ind)
                        ficha_segura = re.sub(r'[^a-zA-Z0-9]', '', ficha)
                        out_name = f"{id_evento}_{ficha_segura}_{p.replace('.docx', '')}.docx"
                        doc.save(os.path.join(evento_dir, out_name))
                        docs_gen.append(out_name)
                    except Exception as ex:
                        print(f"Error en individual {p}: {ex}")

        ctx_grp = {
            "clave_evento": id_evento,
            "nombre_evento": nombre_curso,
            "nombre_curso": nombre_curso,
            "duracion": duracion_curso,
            "nombre_instructor": nombre_instructor,
            "ficha_instructor": ficha_instructor,
            "fecha_inicio": f_inicio,
            "fecha_termino": f_termino,
            "dia_inicio": dia_i,
            "mes_inicio": mes_i,
            "anio_inicio": anio_i,
            "dia_termino": dia_t,
            "mes_termino": mes_t,
            "anio_termino": anio_t,
            "lista_participantes": lista_participantes,
            "tipo_curso": tipo_curso
        }

        for p in plantillas_grp:
            t_path = os.path.join('templates', p)
            if os.path.exists(t_path):
                if p.endswith('.docx'):
                    try:
                        doc = DocxTemplate(t_path)
                        doc.render(ctx_grp)
                        out_name = f"{id_evento}_EVENTO_{p.replace('.docx', '')}.docx"
                        doc.save(os.path.join(evento_dir, out_name))
                        docs_gen.append(out_name)
                    except Exception as ex:
                        print(f"Error en grupal {p}: {ex}")
                elif p.endswith('.xlsx'):
                    try:
                        import openpyxl
                        participantes = ctx_grp.get('lista_participantes', [])
                        baja_fichas = [h.ficha_trabajador for h in HistorialCapacitacion.query.filter_by(id_evento=id_evento, estado='BAJA').all()]
                        participantes = [p for p in participantes if p['ficha'] not in baja_fichas]
                        chunks = [participantes[i:i + 5] for i in range(0, max(1, len(participantes)), 5)]
                        for chunk_idx, chunk in enumerate(chunks):
                            wb = openpyxl.load_workbook(t_path)
                            if 'Propuesta' in wb.sheetnames:
                                ws = wb['Propuesta']
                                if ws['D9'].value and 'nombre_evento' in str(ws['D9'].value):
                                    ws['D9'] = ctx_grp.get('nombre_evento', '')
                                if ws['I54'].value and 'nombre_supervisor' in str(ws['I54'].value):
                                    inst_name = ctx_grp.get('nombre_instructor', '')
                                    inst_ficha = ctx_grp.get('ficha_instructor', '')
                                    ws['I54'] = f"{inst_name} F-{inst_ficha}"
                                ws['I30'] = ''
                                ws['I31'] = ''
                                ws['M30'] = ''
                                start_col = 9 
                                for idx, part in enumerate(chunk):
                                    ws.cell(row=30, column=start_col + idx).value = part.get('ficha', '')
                                    ws.cell(row=31, column=start_col + idx).value = part.get('nombre_completo', '')
                            suffix = f" ({chunk_idx + 1})" if chunk_idx > 0 else ""
                            out_name = f"{id_evento}_EVENTO_{p.replace('.xlsx', '')}{suffix}.xlsx"
                            wb.save(os.path.join(evento_dir, out_name))
                            docs_gen.append(out_name)
                    except Exception as ex:
                        print(f"Error en grupal xlsx {p}: {ex}")

        curso = Curso.query.filter_by(id_evento=id_evento).first()
        if not curso:
            curso = Curso(id_evento=id_evento, nombre_evento=nombre_curso, fase_actual=4, tipo_curso=tipo_curso)
            db.session.add(curso)
        else:
            curso.fase_actual = 4
            curso.nombre_evento = nombre_curso
            curso.tipo_curso = tipo_curso

        for part in historial:
            existe = HistorialCapacitacion.query.filter_by(id_evento=id_evento, ficha_trabajador=part['ficha_trabajador']).first()
            if not existe:
                nuevo = HistorialCapacitacion(id_evento=id_evento, ficha_trabajador=part['ficha_trabajador'], nombre_trabajador=part['nombre_trabajador'])
                db.session.add(nuevo)
        
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"¡Éxito! Se generaron {len(docs_gen)} documentos.",
            "data": docs_gen
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error del Motor: {str(e)}"}), 500

def download_docs(id_evento):
    try:
        id_ev = str(id_evento).strip()
        if '..' in id_ev or '/' in id_ev or '\\' in id_ev:
            return jsonify({"status": "error", "message": "ID Inválido"}), 400
            
        evento_dir = os.path.join('outputs', id_ev)
        if not os.path.exists(evento_dir):
            return jsonify({"status": "error", "message": "Sin documentos generados."}), 404

        all_files = os.listdir(evento_dir)
        if not all_files:
            return jsonify({"status": "error", "message": "No hay documentos."}), 404

        docx_files = [f for f in all_files if f.endswith('.docx')]
        xlsx_files = [f for f in all_files if f.endswith('.xlsx')]

        gotenberg_url = os.environ.get('GOTENBERG_URL', 'http://gotenberg:3000')

        for docx in docx_files:
            filepath = os.path.join(evento_dir, docx)
            with open(filepath, 'rb') as f:
                try:
                    res = requests.post(f"{gotenberg_url}/forms/libreoffice/convert", files={'files': (docx, f)}, timeout=300)
                    if res.status_code == 200:
                        pdf_path = os.path.join(evento_dir, docx.replace('.docx', '.pdf'))
                        with open(pdf_path, 'wb') as pdf_file:
                            pdf_file.write(res.content)
                except Exception as e:
                    print(f"Error convirtiendo {docx} a PDF: {e}")

        pdf_files = sorted([f for f in os.listdir(evento_dir) if f.endswith('.pdf')])
        merger = PdfWriter()
        for pdf in pdf_files:
            merger.append(os.path.join(evento_dir, pdf))

        m_path = os.path.join(evento_dir, f"{id_ev}_PDF_Maestro.pdf")
        if pdf_files:
            merger.write(m_path)
        merger.close()

        mem_file = io.BytesIO()
        with zipfile.ZipFile(mem_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(m_path):
                zf.write(m_path, f"{id_ev}_PDF_Maestro.pdf")
            for docx in docx_files:
                zf.write(os.path.join(evento_dir, docx), docx)
            for xlsx in xlsx_files:
                zf.write(os.path.join(evento_dir, xlsx), xlsx)
        mem_file.seek(0)

        return send_file(mem_file, mimetype='application/zip', as_attachment=True, download_name=f"Expediente_{id_ev}.zip")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def extract_pdf():
    if 'file' not in request.files: return jsonify({"status": "error", "message": "Sin archivo adjunto"}), 400
    file = request.files['file']
    if not file.filename.endswith('.pdf'): return jsonify({"status": "error", "message": "Solo .pdf"}), 400

    try:
        pdf_bytes = io.BytesIO(file.read())
        with pdfplumber.open(pdf_bytes) as pdf:
            texto_completo = ""
            for page in pdf.pages: texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"

            txt_flat = re.sub(r'\s+', ' ', texto_completo.upper().replace('|', ' '))

            id_m = re.search(r"ID SIRHN GENERADO\s*(\d+)", txt_flat)
            id_ev = id_m.group(1) if id_m else "0"

            nom_m = re.search(r"TIPO DE FORMACI[OÓ]N\s+(.*?)\s+(?:CURSO|EVENTO|TALLER)", txt_flat)
            nombre_ev = nom_m.group(1).strip() if nom_m else "SIN DATO"

            f_matches = re.findall(r"FECHA DE INICIO\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}/\d{2}/\d{4})\s*(\d+)", txt_flat)
            if not f_matches:
                f_matches = re.findall(r"(\d{2}/\d{2}/\d{4})\s*(\d{2}/\d{2}/\d{4})\s*(\d+)", txt_flat)
            if f_matches:
                f_ini, f_term, dur = f_matches[-1]
            else:
                f_ini, f_term, dur = "SIN DATO", "SIN DATO", "0"

            inst_m = re.search(r"HORARIO.*?\d{2}:\d{2}.*?\s([A-ZÑ\s]+?)\s*F-?.*?(\d{5,6})", txt_flat)
            n_inst = inst_m.group(1).strip() if inst_m else "SIN DATO"
            f_inst = inst_m.group(2).strip() if inst_m else "SIN DATO"

            val_m = re.search(r"ID SIRHN GENERADO\s*\d+\s+[A-ZÑ\s]+?F-?\d{5,6}\s+([A-ZÑ\s]+?)\s*F-?(\d{5,6})", txt_flat)
            n_sup = val_m.group(1).strip() if val_m else "SIN DATO"
            f_sup = val_m.group(2).strip() if val_m else "SIN DATO"

            try:
                d_i, m_i, a_i = f_ini.split('/')
            except:
                d_i, m_i, a_i = "", "", ""
            try:
                d_t, m_t, a_t = f_term.split('/')
            except:
                d_t, m_t, a_t = "", "", ""

            def dividir_nombre(full_name):
                parts = str(full_name).strip().split()
                if not parts: return "", "", ""
                prefixes = {"DE", "LA", "LAS", "DEL", "LOS", "MAC", "SAN", "SANTA", "Y"}
                g, c = [], ""
                for p in parts:
                    if p.upper() in prefixes:
                        c += p + " "
                    else:
                        c += p;
                        g.append(c);
                        c = ""
                if len(g) == 1:
                    return g[0], "", ""
                elif len(g) == 2:
                    return g[0], "", g[1]
                else:
                    return g[0], g[1], " ".join(g[2:])

            participantes = []
            for page in pdf.pages:
                for tabla in page.extract_tables():
                    if tabla and len(tabla) > 0 and "Ficha" in str(tabla[0]):
                        for fila in tabla[1:]:
                            if len(fila) >= 5 and fila[1]:
                                ficha = str(fila[1]).replace('\n', '').strip()
                                if ficha.isdigit():
                                    pat, mat, nom = dividir_nombre(str(fila[2]).replace('\n', ' '))
                                    participantes.append({
                                        "ID": id_ev,
                                        "NOMBRE DEL EVENTO": nombre_ev,
                                        "FICHA": ficha,
                                        "PRIMER APELLIDO": pat, "SEGUNDO APELLIDO": mat, "NOMBRE": nom,
                                        "NIVEL": str(fila[3]).replace('\n', '').strip(),
                                        "CATEGORIA": str(fila[4]).replace('\n', ' ').strip(),
                                        "DIA I": d_i, "MES I": m_i, "AÑO I": a_i,
                                        "DIA T": d_t, "MES T": m_t, "AÑO T": a_t,
                                        "DURACION HORAS": dur,
                                        "NOMBRE INSTRUCTOR": n_inst.title(),
                                        "FICHA INSTRUCTOR": f_inst,
                                        "NOMBRE SUPERVISOR": n_sup.title(),
                                        "FICHA SUPERVISOR": f_sup
                                    })

        mem_file = io.BytesIO()
        with pd.ExcelWriter(mem_file, engine='openpyxl') as writer:
            if participantes:
                pd.DataFrame(participantes).to_excel(writer, sheet_name='Base_Datos', index=False)
            else:
                pd.DataFrame([{"Error": "No se encontraron trabajadores"}]).to_excel(writer, sheet_name='Errores')

        mem_file.seek(0)
        
        response = send_file(mem_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=f"Guia de Asistencia - {id_ev}.xlsx")
        
        # Expose custom header for frontend validation
        response.headers['X-Workers-Count'] = str(len(participantes)) if participantes else "0"
        response.headers['Access-Control-Expose-Headers'] = 'X-Workers-Count'
        
        return response
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
