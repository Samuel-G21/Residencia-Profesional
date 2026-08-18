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

if __name__ == '__main__':
    app.run(host='0.0.0.0', ports=5000, debug=True)