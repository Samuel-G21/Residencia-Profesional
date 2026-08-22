import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Se habilitan los CORS para que la parte de Frontends pueda realizar peticiones
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "success",
        "message": "Sistema de PEMEX en correcto funcionamiento"
    }), 200

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)