import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from docxtpl import DocxTemplate

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)