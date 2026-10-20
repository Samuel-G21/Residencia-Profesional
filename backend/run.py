"""
Punto de entrada principal de la aplicacion Flask (Backend).

Guia para practicantes:
- En desarrollo local puedes ejecutar `python run.py` para levantar el servidor en el puerto 5000.
- En produccion (dentro del contenedor Docker), Gunicorn importa el objeto `app` desde este archivo
  utilizando el comando definido en el Dockerfile: `gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 run:app`.
"""
from app import create_app

# Instancia global de la aplicacion creada mediante el patron Application Factory
app = create_app()

if __name__ == '__main__':
    # Ejecucion directa para pruebas locales (habilita recarga automatica con debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
