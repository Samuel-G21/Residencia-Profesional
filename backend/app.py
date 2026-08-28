import os
import subprocess
import zipfile
import io
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from docxtpl import DocxTemplate
from pypdf import PdfWriter
import io
import re
import pdfplumber
from flask import send_file

app = Flask(__name__)

# Se habilitan los CORS para que la parte de Frontends pueda realizar peticiones
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "success",
        "message": "Sistema de PEMEX en correcto funcionamiento"
    }), 200

# Endpoint para subir el archivo Excel
@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    # 1. Validar que la petición traiga un archivo
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No se encontró ningún archivo adjunto"}), 400
    
    file = request.files['file']
    
    # 2. Validar que el archivo no esté vacío y sea .xlsx
    if file.filename == '':
        return jsonify({"status": "error", "message": "No seleccionaste ningún archivo"}), 400
        
    if not file.filename.endswith('.xlsx'):
        return jsonify({"status": "error", "message": "Formato inválido. Por favor sube un archivo .xlsx"}), 400
        
    try:
        # 3. Leer el Excel directamente en memoria
        df = pd.read_excel(file)
        
        # --- AQUÍ ESTABAN LAS LÍNEAS PERDIDAS ---
        # Asegúrate de que estos sean los nombres exactos en tu archivo Excel
        columna_id = 'ID' # Si en tu Excel dice 'Clave del Evento', cámbialo aquí
        columna_nombre = 'NOMBRE DEL EVENTO'
        
        # 4. Extraer solo las columnas de interés y eliminar los duplicados
        cursos_df = df[[columna_id, columna_nombre]].drop_duplicates()
        
        # 5. Convertir a un formato amigable para React (Diccionario/JSON)
        cursos_lista = cursos_df.rename(columns={columna_id: 'id', columna_nombre: 'nombre'}).to_dict('records')
        
        # 6. Retornar los datos
        return jsonify({
            "status": "success",
            "data": cursos_lista
        }), 200

    except Exception as e:
        # Capturar cualquier error
        return jsonify({"status": "error", "message": f"Error al procesar el Excel: {str(e)}"}), 500

# Endpoint para generar documentos
@app.route('/api/generate-docs', methods=['POST'])
def generate_docs():
    # Validacion de peticion con archivo Excel y el ID del evento
    if 'file' not in request.files or 'id_evento' not in request.form:
        return jsonify({"status": "error", "message": "Falta el archivo Excel o el ID del evento"}), 400

    file = request.files['file']
    id_evento = request.form['id_evento']

    try:
        # Lectura del archivo Excel
        df = pd.read_excel(file)

        # Asegurarnos de que el ID en Pandas y el de la petición sean texto para evitar errores de búsqueda
        columna_id = 'ID' # O puede ser 'Clave del Evento'
        df[columna_id] = df[columna_id].astype(str)
        id_evento_str = str(id_evento).strip()

        # Filtrar a los trabajadores que pertenecen al evento
        trabajadores_curso = df[df[columna_id] == id_evento_str]

        if trabajadores_curso.empty:
            return jsonify({"status": "error", "message": f"No se encontraron trabajadores para el curso {id_evento}"}), 404

        # Procesar y generar Word por cada trabajador
        documentos_generados =[]

        # Usaremos el formato SCPM-04 como prueba
        template_path = os.path.join('templates', 'SCPM-04.docx')

        if not os.path.exists(template_path):
            return jsonify({"status": "error", "message": "Falta colocar el archivo SCPM-04.docx en la carpeta templates/"}), 500
        
        for index, row in trabajadores_curso.iterrows():
            # Aplicar reglas de limpieza de datos
            ficha = str(int(row['FICHA'])) if pd.notna(row['FICHA']) else ""
            nombres = str(row['NOMBRE']).strip().title() if pd.notna(row['NOMBRE']) else ""
            paterno = str(row['PRIMER APELLIDO']).strip().title() if pd.notna(row['PRIMER APELLIDO']) else ""
            materno = str(row['SEGUNDO APELLIDO']).strip().title() if pd.notna(row['SEGUNDO APELLIDO']) else ""
            nombre_completo = f"{paterno} {materno} {nombres}".strip()

            dia_inicio = str(row['dia i']).zfill(2) if pd.notna(row['dia i']) else ""
            mes_inicio = str(row['mes i']).zfill(2) if pd.notna(row['mes i']) else ""
            anio_inicio = str(row['año i']).split('.')[0] if pd.notna(row['año i']) else ""

            # Construir el contexto para Jinja2
            context = {
                "ficha": ficha,
                "apellido_paterno": paterno,
                "apellido_materno": materno,
                "nombres": nombres,
                "nombre_completo": nombre_completo,
                "dia_inicio": dia_inicio,
                "mes_inicio": mes_inicio,
                "anio_inicio": anio_inicio,
                "nombre_curso": str(row['NOMBRE DEL EVENTO']).strip().upper() if pd.notna(row['NOMBRE DEL EVENTO']) else ""
            }

            # Implantamos los datos en el word
            doc = DocxTemplate(template_path)
            doc.render(context)

            # Guardar archivo generado en /outputs (Ejemplo: 50693032 SCPM-04_123456.docx)
            nombre_archivo = f"{id_evento_str} SCPM-04.docx"
            output_path = os.path.join('outputs', nombre_archivo)

            documentos_generados.append(nombre_archivo)

        return jsonify({
            "status": "success",
            "message": f"Se generaron {len(documentos_generados)} documentos SCPM-04.",
            "data": documentos_generados
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al generar los documentos: {str(e)}"
        }), 500

@app.route('/api/download-docs/<id_evento>', methods=['GET'])
def download_docs(id_evento):
    try:
        output_dir = 'outputs'
        id_evento_str = str(id_evento).strip()
        
        # 1. Encontrar todos los Word generados previamente para este evento
        docx_files = [f for f in os.listdir(output_dir) if f.startswith(id_evento_str) and f.endswith('.docx')]
        
        if not docx_files:
            return jsonify({"status": "error", "message": f"No se encontraron documentos Word para el evento {id_evento_str}"}), 404

        pdf_files = []
        
        # 2. Convertir cada DOCX a PDF usando LibreOffice en el contenedor
        for docx in docx_files:
            docx_path = os.path.join(output_dir, docx)
            # Llamada al sistema Linux para convertir el archivo
            subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, docx_path], check=True)
            
            pdf_filename = docx.replace('.docx', '.pdf')
            pdf_files.append(pdf_filename)

        # 3. Unir todos los PDFs en un PDF Maestro
        merger = PdfWriter()
        for pdf in pdf_files:
            merger.append(os.path.join(output_dir, pdf))

        maestro_filename = f"{id_evento_str}_PDF_Maestro.pdf"
        maestro_path = os.path.join(output_dir, maestro_filename)
        merger.write(maestro_path)
        merger.close()

        # 4. Crear el archivo ZIP en memoria RAM
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # A) Agregar el PDF Maestro listo para imprimir
            zf.write(maestro_path, maestro_filename)
            # B) Agregar los archivos originales DOCX
            for docx in docx_files:
                zf.write(os.path.join(output_dir, docx), docx)
        
        memory_file.seek(0)

        # 5. Limpieza del servidor: Borrar PDFs individuales y maestro (conservando los DOCX originales)
        for pdf in pdf_files:
            os.remove(os.path.join(output_dir, pdf))
        os.remove(maestro_path)

        # 6. Retornar el ZIP descargable
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"Expediente_{id_evento_str}.zip"
        )

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al empaquetar los documentos: {str(e)}"}), 500

@app.route('/api/extract-pdf', methods=['POST'])
def extract_pdf():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No se encontro ningun archivo adjunto"}), 400

    file = request.files['file']

    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"status": "error", "message": "Formato invalido. Por favor sube un archivo .pdf"}), 400
    
    try:
        datos_eventos = {}
        participantes = []

        # LECTURA DE PDF
        with pdfplumber.open(file) as pdf:
            texto_completo =""
            for page in pdf.pages:
                texto_completo += page.extract_text() + "\n"
            
            # Extraccion de cabecera
            id_sirhn = re.search (r"ID SIRHN GENERADO\s*(\d+)", texto_completo)
            datos_eventos['ID_Evento (SIRHN)'] = id_sirhn.group(1) if id_sirhn else ""

            nombre_evento = re.search(r"Nombre del\s*\n?(.+?)\s*\n?Tipo de Formación", texto_completo, re.IGNORECASE)
            datos_evento['Nombre del Evento'] = nombre_evento.group(1).strip() if nombre_evento else ""
            
            fecha_inicio = re.search(r"Fecha de inicio\s*(\d{2}/\d{2}/\d{4})", texto_completo)
            datos_evento['Fecha Inicio'] = fecha_inicio.group(1) if fecha_inicio else ""
            
            # Extraer Tabla de Participantes
            for page in pdf.pages:
                tablas = page.extract_tables()
                for tabla in tablas:
                    if len(tabla) > 0 and tabla[0] and "Ficha" in str(tabla[0]):
                        for fila in tabla[1:]:
                            if len(fila) >= 5 and fila[1]: 
                                ficha = str(fila[1]).replace('\n', '').strip()
                                if ficha.isdigit():
                                    participantes.append({
                                        "No.": fila[0].replace('\n', '').strip() if fila[0] else "",
                                        "Ficha": ficha,
                                        "Nombre": fila[2].replace('\n', ' ').strip() if fila[2] else "",
                                        "Nivel": fila[3].replace('\n', '').strip() if fila[3] else "",
                                        "Categoría": fila[4].replace('\n', ' ').strip() if fila[4] else ""
                                    })
        
        # Crear el archivo Excel en la memoria RAM (sin guardarlo en el disco duro)
        memory_file = io.BytesIO()
        df_evento = pd.DataFrame([datos_evento])
        df_participantes = pd.DataFrame(participantes)
        
        with pd.ExcelWriter(memory_file, engine='openpyxl') as writer:
            df_evento.to_excel(writer, sheet_name='Datos Generales', index=False)
            df_participantes.to_excel(writer, sheet_name='Participantes', index=False)
            
        memory_file.seek(0)
        
        # Enviar el archivo Excel de regreso al cliente (React o Postman)
        nombre_descarga = f"Extraccion_{datos_evento.get('ID_Evento (SIRHN)', 'SCPM01')}.xlsx"
        
        return send_file(
            memory_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=nombre_descarga
        )

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar el PDF: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)