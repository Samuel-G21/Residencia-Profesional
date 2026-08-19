import pandas as pd
from flask import Flask, jsoninfy
from flask_cors import CORS

app = Flask(__name__)

# Se habilitan los CORS para que la parte de Frontends pueda realizar peticiones
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return jsoninfy({
        "status": "success",
        "message": "Sistema de PEMEX en correcto funcionamiento"
    }), 200

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    # Validar que la peticion traiga un archivo
    if 'file' not in request.files:
        return jsoninfy({
            "status": "error",
            "message": "No se envio ningun archivo adjunto"
        }), 400
    
    file = request.file['file']

    # Validar que el archivo no este vacio y que sea .xlsx
    if file.filename =='':
        return jsoninfy({"status": "error", "message": "No selecionaste ningun archivo"}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsoninfy({"status": "error", "message": "Formato invalido. Por favor sube un .xlsx"}), 400

    try:
        # leer el excel directamente en memoeria (sin guardarlo en el disco duro)
        df = pd.read_excel(file)

        # Aqui se pueden ajustar nos nombres si el excel viene distinto
        colmna_id = 'ID'
        columna_nombre = 'NOMBRE DEL EVENTO'

        '''
            Extraccion de las columnas de interes y eliminacion de duplicados
            (Ya que un evento tendra muchas filas porque tienen muchos trabajadores)
        '''
        cursos_df = df[[colmna_id, columna_nombre]].drop_duplicates()

        # Convertir en formato para React
        curso_lista = cursos_df.rename(colums={colmna_id: 'id', columna_nombre: 'nombre'}).to_dict('records')

        return jsoninfy({
            "status": "success",
            "data": curso_lista
        }), 200

    except Exception as e:
        # Se captura cualquier error
        return jsoninfy({
            "status": "error",
            "message": f"Error al procesar el Excel: {str(e)}" 
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', ports=5000, debug=True)