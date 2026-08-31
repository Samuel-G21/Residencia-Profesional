import os
import subprocess
import zipfile
import io
import shutil
import pandas as pd
import pymysql
import re
import pdfplumber
from contextlib import closing
from flask import send_file, Flask, request, jsonify
from flask_cors import CORS
from docxtpl import DocxTemplate
from pypdf import PdfWriter

app = Flask(__name__)
# Habilitamos CORS para la comunicación con React
CORS(app)

# ==========================================
# 1. CONEXIÓN A BASE DE DATOS
# ==========================================
def get_db_connection():
    try:
        conexion = pymysql.connect(
            host=os.getenv('DB_HOST', 'db'),
            user=os.getenv('DB_USER', 'pemex_user'),
            password=os.getenv('DB_PASSWORD', 'pemex_password'),
            database=os.getenv('DB_NAME', 'pemex_db'),
            cursorclass=pymysql.cursors.DictCursor
        )
        return conexion
    except Exception as e:
        print(f"Error conectando a la BD: {e}")
        return None

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Sistema de PEMEX Activo (Nivel Dios)"}), 200

# ==========================================
# 2. CARGA Y LECTURA DE EXCEL
# ==========================================
@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No se encontró ningún archivo adjunto"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.xlsx'):
        return jsonify({"status": "error", "message": "Formato inválido (.xlsx requerido)"}), 400
        
    try:
        df = pd.read_excel(file)
        columna_id = 'ID'
        columna_nombre = 'NOMBRE DEL EVENTO'
        
        if columna_id not in df.columns or columna_nombre not in df.columns:
            return jsonify({"status": "error", "message": "El Excel no tiene las columnas esperadas"}), 400

        cursos_df = df[[columna_id, columna_nombre]].drop_duplicates()
        cursos_lista = cursos_df.rename(columns={columna_id: 'id', columna_nombre: 'nombre'}).to_dict('records')
        
        return jsonify({"status": "success", "data": cursos_lista}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar el Excel: {str(e)}"}), 500

# ==========================================
# 3. MOTOR DE INYECCIÓN (WORD) - INDIVIDUALES Y GRUPALES
# ==========================================
def safe_str(val):
    if pd.isna(val) or val == '':
        return ""
    try:
        f_val = float(val)
        if f_val.is_integer():
            return str(int(f_val))
        return str(val).strip()
    except (ValueError, TypeError):
        return str(val).strip()

@app.route('/api/generate-docs', methods=['POST'])
def generate_docs():
    if 'file' not in request.files or 'id_evento' not in request.form:
        return jsonify({"status": "error", "message": "Faltan datos de entrada"}), 400

    file = request.files['file']
    id_evento = re.sub(r'[^a-zA-Z0-9_-]', '', str(request.form['id_evento']).strip())

    try:
        df = pd.read_excel(file)
        df = df.fillna('')
        columna_id = 'ID'
        
        if columna_id not in df.columns:
            return jsonify({"status": "error", "message": "Falta la columna 'ID'"}), 400

        df[columna_id] = df[columna_id].apply(safe_str)
        trabajadores_curso = df[df[columna_id] == id_evento]
        
        if trabajadores_curso.empty:
            return jsonify({"status": "error", "message": f"Sin trabajadores para el curso {id_evento}"}), 404

        # Crear/Limpiar carpeta temporal
        evento_dir = os.path.join('outputs', id_evento)
        os.makedirs(evento_dir, exist_ok=True)
        for f in os.listdir(evento_dir):
            os.remove(os.path.join(evento_dir, f))

        # --- CARGA DEL CATÁLOGO MAESTRO DE CURPS ---
        diccionario_curps = {}
        ruta_catalogo = os.path.join('catalogos', 'CURP.xlsx')
        if os.path.exists(ruta_catalogo):
            try:
                df_curps = pd.read_excel(ruta_catalogo)
                df_curps['FICHA'] = df_curps['FICHA'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                df_curps['CURP'] = df_curps['CURP'].astype(str).str.strip().str.upper()
                diccionario_curps = dict(zip(df_curps['FICHA'], df_curps['CURP']))
            except Exception as e:
                print(f"Advertencia: Error al cargar catálogo de CURPs: {e}")

        # Variables Generales del Evento
        primer_registro = trabajadores_curso.iloc[0]
        nombre_curso = str(primer_registro.get('NOMBRE DEL EVENTO', '')).strip().upper()
        duracion_curso = safe_str(primer_registro.get('DURACION HORAS', ''))
        
        dia_inicio_evt = safe_str(primer_registro.get('dia i', '')).zfill(2)
        mes_inicio_evt = safe_str(primer_registro.get('mes i', '')).zfill(2)
        anio_inicio_evt = safe_str(primer_registro.get('año i', ''))
        dia_term_evt = safe_str(primer_registro.get('dia T', '')).zfill(2)
        mes_term_evt = safe_str(primer_registro.get('mes T', '')).zfill(2)
        anio_term_evt = safe_str(primer_registro.get('año T', ''))
        
        fecha_inicio_completa = f"{dia_inicio_evt}/{mes_inicio_evt}/{anio_inicio_evt}" if anio_inicio_evt else ""
        fecha_termino_completa = f"{dia_term_evt}/{mes_term_evt}/{anio_term_evt}" if anio_term_evt else ""

        nombre_instructor = str(primer_registro.get('NOMBRE INSTRUCTOR', '')).strip().title()
        ficha_instructor = safe_str(primer_registro.get('FICHA INSTRUCTOR', ''))
        nombre_supervisor = str(primer_registro.get('NOMBRE SUPERVISOR', '')).strip().title()
        ficha_supervisor = safe_str(primer_registro.get('FICHA SUPERVISOR', ''))

        # Separación de Plantillas
        plantillas_individuales = [
            '1. Cédula registro actualizado 2025 COMBIANADA.docx', 
            '2. Constancias de Habilidades DC-3 2026 COMBINADA.docx', 
            'SCPM-04 COMBINADA.docx', 
            'SCPM-04.docx', 
            'SCPM-06 COMBINADA.docx'
        ]
        plantillas_evento = [
            '5. Carta Compromiso Instructor 2026 COMBINADA.docx', 
            'FVC.docx', 
            'Informe Técnico Instructor 2025.docx', 
            'SCPM-05 2025.docx'
        ]

        documentos_generados = []
        historial_data = []
        lista_participantes = []
        
        # A) INYECCIÓN POR TRABAJADOR (INDIVIDUAL)
        for index, row in trabajadores_curso.iterrows():
            ficha = safe_str(row.get('FICHA', ''))
            nombres = str(row.get('NOMBRE(S)', '')).strip().title()
            paterno = str(row.get('PRIMER APELLIDO', '')).strip().title()
            materno = str(row.get('SEGUNDO APELLIDO', '')).strip().title()
            nombre_completo = f"{paterno} {materno} {nombres}".strip()
            
            # Buscar CURP en catálogo maestro
            curp = diccionario_curps.get(ficha, "CURP_NO_ENCONTRADA")
            
            # Datos de la fila actual para la tabla maestra SCPM-05
            if ficha:
                lista_participantes.append({
                    "ficha": ficha,
                    "nombre_completo": nombre_completo,
                    "categoria": str(row.get('CATEGORÍA', row.get('CATEGORIA', ''))).strip(),
                    "nivel": safe_str(row.get('NIVEL', '')),
                    "departamento": str(row.get('DEPARTAMENTO', '')).strip()
                })
                historial_data.append((id_evento, ficha, nombre_completo))

            context_individual = {
                "ficha": ficha, "ficha_trabajador": ficha, 
                "apellido_paterno": paterno, 
                "apellido_materno": materno,
                "nombre": nombres, "nombres": nombres, 
                "nombre_completo": nombre_completo, "nombre_trabajador": nombre_completo,
                "curp": curp,
                "nombre_evento": nombre_curso, "clave_evento": id_evento,
                "duracion": duracion_curso,
                "fecha_inicio": fecha_inicio_completa, "fecha_termino": fecha_termino_completa,
                "nombre_instructor": nombre_instructor, "ficha_instructor": ficha_instructor,
                "nombre_supervisor": nombre_supervisor, "ficha_supervisor": ficha_supervisor
            }

            for nombre_plantilla in plantillas_individuales:
                template_path = os.path.join('templates', nombre_plantilla)
                if os.path.exists(template_path):
                    try:
                        doc = DocxTemplate(template_path)
                        doc.render(context_individual)
                        nombre_limpio = nombre_plantilla.replace('.docx', '')
                        ficha_segura = re.sub(r'[^a-zA-Z0-9]', '', ficha)
                        nombre_archivo = f"{id_evento}_{ficha_segura}_{nombre_limpio}.docx"
                        output_path = os.path.join(evento_dir, nombre_archivo)
                        doc.save(output_path)
                        documentos_generados.append(nombre_archivo)
                    except Exception as ex:
                        print(f"Error renderizando {nombre_plantilla} ficha {ficha}: {ex}")

        # B) INYECCIÓN GRUPAL (POR EVENTO)
        context_evento = {
            "clave_evento": id_evento,
            "nombre_evento": nombre_curso,
            "duracion": duracion_curso,
            "fecha_inicio": fecha_inicio_completa,
            "fecha_termino": fecha_termino_completa,
            "dia_inicio": dia_inicio_evt, "mes_inicio": mes_inicio_evt, "anio_inicio": anio_inicio_evt,
            "dia_termino": dia_term_evt, "mes_termino": mes_term_evt, "anio_termino": anio_term_evt,
            "nombre_instructor": nombre_instructor, "ficha_instructor": ficha_instructor,
            "nombre_supervisor": nombre_supervisor, "ficha_supervisor": ficha_supervisor,
            "lista_participantes": lista_participantes # <- INYECCIÓN DE LA TABLA MAESTRA
        }
        
        for nombre_plantilla in plantillas_evento:
            template_path = os.path.join('templates', nombre_plantilla)
            if os.path.exists(template_path):
                try:
                    doc = DocxTemplate(template_path)
                    doc.render(context_evento)
                    nombre_limpio = nombre_plantilla.replace('.docx', '')
                    nombre_archivo = f"{id_evento}_EVENTO_{nombre_limpio}.docx" 
                    output_path = os.path.join(evento_dir, nombre_archivo)
                    doc.save(output_path)
                    documentos_generados.append(nombre_archivo)
                except Exception as ex:
                    print(f"Error renderizando {nombre_plantilla}: {ex}")

        # C) ALMACENAMIENTO EN BASE DE DATOS
        conexion = get_db_connection()
        if conexion:
            with closing(conexion):
                with conexion.cursor() as cursor:
                    cursor.execute("INSERT IGNORE INTO cursos (id_evento, nombre_evento) VALUES (%s, %s)", (id_evento, nombre_curso))
                    if historial_data:
                        cursor.executemany("INSERT INTO historial_capacitacion (id_evento, ficha_trabajador, nombre_trabajador) VALUES (%s, %s, %s)", historial_data)
                conexion.commit()

        return jsonify({
            "status": "success",
            "message": f"¡Éxito! Se generaron {len(documentos_generados)} documentos.",
            "data": documentos_generados
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error del Motor: {str(e)}"}), 500


# ==========================================
# 4. COLA DE IMPRESIÓN (PDF & ZIP)
# ==========================================
@app.route('/api/download-docs/<id_evento>', methods=['GET'])
def download_docs(id_evento):
    try:
        id_evento_str = re.sub(r'[^a-zA-Z0-9_-]', '', str(id_evento).strip())
        evento_dir = os.path.join('outputs', id_evento_str)
        
        if not os.path.exists(evento_dir):
            return jsonify({"status": "error", "message": "No hay documentos generados para este evento."}), 404

        docx_files = [f for f in os.listdir(evento_dir) if f.endswith('.docx')]
        if not docx_files:
            return jsonify({"status": "error", "message": "No hay Word en el directorio."}), 404

        my_env = os.environ.copy()
        my_env['HOME'] = '/tmp' # Previene crasheos de LibreOffice

        # Procesamiento masivo por lotes (Chunks)
        chunk_size = 30
        for i in range(0, len(docx_files), chunk_size):
            chunk = docx_files[i:i+chunk_size]
            subprocess.run(
                ['libreoffice', '--headless', '--nologo', '--nofirststartwizard', '--convert-to', 'pdf', '--outdir', evento_dir] + chunk, 
                cwd=evento_dir, check=True, env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        pdf_files = [f for f in os.listdir(evento_dir) if f.endswith('.pdf')]
        
        # Unificación del PDF Maestro
        merger = PdfWriter()
        for pdf in sorted(pdf_files): 
            merger.append(os.path.join(evento_dir, pdf))

        maestro_filename = f"{id_evento_str}_PDF_Maestro.pdf"
        maestro_path = os.path.join(evento_dir, maestro_filename)
        if len(pdf_files) > 0:
            merger.write(maestro_path)
        merger.close()

        # Empaquetado ZIP
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(maestro_path):
                zf.write(maestro_path, maestro_filename)
            for docx in docx_files:
                zf.write(os.path.join(evento_dir, docx), docx)
        memory_file.seek(0)

        # Limpieza para no saturar servidor
        shutil.rmtree(evento_dir, ignore_errors=True)

        return send_file(
            memory_file, mimetype='application/zip', as_attachment=True, download_name=f"Expediente_{id_evento_str}.zip"
        )
    except Exception as e:
        if 'evento_dir' in locals() and os.path.exists(evento_dir):
            shutil.rmtree(evento_dir, ignore_errors=True)
        return jsonify({"status": "error", "message": f"Error en empaquetado: {str(e)}"}), 500


# ==========================================
# 5. MOTOR MAESTRO DE EXTRACCIÓN DE PDF (SCPM-01) CON NLP BÁSICO
# ==========================================
@app.route('/api/extract-pdf', methods=['POST'])
def extract_pdf():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Sin archivo adjunto"}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"status": "error", "message": "Solo archivos .pdf"}), 400
    
    try:
        pdf_bytes = io.BytesIO(file.read())
        
        with pdfplumber.open(pdf_bytes) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_completo += page.extract_text(x_tolerance=2, y_tolerance=2) + "\n"
            
            def extraer(patron, texto, default=""):
                match = re.search(patron, texto, re.IGNORECASE)
                return match.group(1).strip() if match else default

            id_evento = extraer(r"ID SIRHN GENERADO\s*\n?(\d+)", texto_completo, "00000000")
            nombre_evento = extraer(r"Nombre del\s*\n(.+?)\s*\nTipo de Formación", texto_completo, "SIN NOMBRE")
            fecha_inicio_str = extraer(r"Fecha de inicio\s*\n?(\d{2}/\d{2}/\d{4})", texto_completo, "//")
            fecha_termino_str = extraer(r"término\s*\n?(\d{2}/\d{2}/\d{4})", texto_completo, "//")
            duracion = extraer(r"Duración\s*\n?\(horas\)\s*\n?(\d+)", texto_completo, "0")
            
            instructor_nombre = extraer(r"Instructor/Proveedor.\s*\n(.+?)\s*\n", texto_completo, "")
            instructor_ficha = extraer(r"Instructor/Proveedor.[\s\S]*?\n(\d{6})\n", texto_completo, "")
            instructor_full = f"{instructor_nombre} {instructor_ficha}".strip()

            try: dia_i, mes_i, anio_i = fecha_inicio_str.split('/')
            except: dia_i, mes_i, anio_i = "", "", ""
                
            try: dia_t, mes_t, anio_t = fecha_termino_str.split('/')
            except: dia_t, mes_t, anio_t = "", "", ""

            # Algoritmo de Agrupación de Apellidos
            def dividir_nombre_compuesto(full_name):
                parts = str(full_name).strip().split()
                if not parts: return "", "", ""
                prefixes = {"DE", "LA", "LAS", "DEL", "LOS", "MAC", "SAN", "SANTA", "Y"}
                grouped, current = [], ""
                for p in parts:
                    if p.upper() in prefixes:
                        current += p + " "
                    else:
                        current += p
                        grouped.append(current)
                        current = ""
                if len(grouped) == 1: return grouped[0], "", ""
                elif len(grouped) == 2: return grouped[0], "", grouped[1] 
                else: return grouped[0], grouped[1], " ".join(grouped[2:])

            participantes = []
            for page in pdf.pages:
                for tabla in page.extract_tables():
                    if len(tabla) > 0 and tabla[0] and "Ficha" in str(tabla[0]):
                        for fila in tabla[1:]:
                            if len(fila) >= 5 and fila[1]:
                                ficha = str(fila[1]).replace('\n', '').strip()
                                if ficha.isdigit():
                                    full_name = str(fila[2]).replace('\n', ' ').strip()
                                    paterno, materno, nombres = dividir_nombre_compuesto(full_name)
                                    nivel = str(fila[3]).replace('\n', '').strip()
                                    categoria = str(fila[4]).replace('\n', ' ').strip()
                                    
                                    participantes.append({
                                        "ID": id_evento,
                                        "NOMBRE DEL EVENTO": nombre_evento,
                                        "FICHA": ficha,
                                        "PRIMER APELLIDO": paterno, "SEGUNDO APELLIDO": materno, "NOMBRE": nombres,
                                        "NIVEL": nivel, "CATEGORIA": categoria,
                                        "dia i": dia_i, "mes i": mes_i, "año i": anio_i,
                                        "dia T": dia_t, "mes T": mes_t, "año T": anio_t,
                                        "INSTRUCTOR": instructor_full, "DURACION HORAS": duracion
                                    })
        
        memory_file = io.BytesIO()
        with pd.ExcelWriter(memory_file, engine='openpyxl') as writer:
            if participantes:
                pd.DataFrame(participantes).to_excel(writer, sheet_name='Hoja1', index=False)
            else:
                pd.DataFrame([{"Error": "No se encontraron trabajadores en la tabla"}]).to_excel(writer, sheet_name='Errores')
            
        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f"Base_Datos_{id_evento}.xlsx")

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error del Motor: {str(e)}"}), 500


# ==========================================
# 6. DASHBOARD Y ESTADÍSTICAS
# ==========================================
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conexion = get_db_connection()
    if not conexion:
        return jsonify({"status": "error", "message": "BD desconectada"}), 500

    try:
        with closing(conexion):
            with conexion.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as total_cursos FROM cursos")
                total_cursos = cursor.fetchone()['total_cursos']

                cursor.execute("SELECT COUNT(*) as total_trabajadores FROM historial_capacitacion")
                total_trabajadores = cursor.fetchone()['total_trabajadores']

                cursor.execute("""
                    SELECT c.nombre_evento, COUNT(h.id) as total_capacitados 
                    FROM cursos c 
                    LEFT JOIN historial_capacitacion h ON c.id_evento = h.id_evento 
                    GROUP BY c.id_evento, c.nombre_evento 
                    ORDER BY total_capacitados DESC LIMIT 5
                """)
                top_cursos = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": {
                "total_cursos": total_cursos,
                "total_trabajadores": total_trabajadores,
                "top_cursos": top_cursos
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error BD: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)