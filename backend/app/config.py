"""
Configuracion global del Backend y conexion a servicios externos.

Guia para practicantes:
- Las variables se leen desde el entorno del sistema o desde un archivo `.env`.
- En Docker, estas variables se inyectan desde `docker-compose.yml`.
- Incluye generacion segura y persistente de `SECRET_KEY` para la firma de tokens JWT.
"""
import os
import time
import secrets
import logging
from dotenv import load_dotenv

# Carga variables definidas en archivo .env (si existe en desarrollo local)
load_dotenv()

_logger = logging.getLogger(__name__)

# Rutas internas para almacenar la llave secreta persistente entre reinicios o workers
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_SECRET_FILE = os.path.join(_BACKEND_DIR, 'instance', 'secret_key')


def _load_or_create_secret_key():
    """
    Devuelve la llave criptografica para firmar y verificar tokens JWT.

    Prioridad: variable de entorno SECRET_KEY -> archivo persistente instance/secret_key.
    Antes existia un valor por defecto fijo ('supersecretkey') que permitia a cualquiera
    falsificar tokens. El archivo se crea de forma atomica (O_EXCL) para que todos los
    workers de Gunicorn compartan exactamente la misma llave.
    """
    env_key = os.getenv('SECRET_KEY')
    if env_key:
        return env_key

    os.makedirs(os.path.dirname(_SECRET_FILE), exist_ok=True)
    try:
        fd = os.open(_SECRET_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        key = secrets.token_hex(32)
        with os.fdopen(fd, 'w') as fh:
            fh.write(key)
        _logger.warning("SECRET_KEY no definida; se genero una llave aleatoria persistente en instance/secret_key.")
        return key
    except FileExistsError:
        # Otro worker de Gunicorn pudo haber creado el archivo hace milisegundos; esperamos a que tenga contenido.
        for _ in range(50):
            with open(_SECRET_FILE, 'r') as fh:
                key = fh.read().strip()
            if key:
                return key
            time.sleep(0.05)
        raise RuntimeError("No se pudo leer instance/secret_key (archivo vacio).")


def _int_env(name, default):
    """Convierte una variable de entorno a entero o devuelve el valor por defecto si no es valida."""
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    """Clase central de configuracion consumida por `app.config.from_object(Config)`."""

    # Llave secreta utilizada para firmar tokens JWT de sesion
    SECRET_KEY = _load_or_create_secret_key()

    # Cadena de conexion a MySQL usando el conector PyMySQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or (
        f"mysql+pymysql://{os.getenv('DB_USER', 'pemex_user')}:{os.getenv('DB_PASSWORD', 'pemex_password')}"
        f"@{os.getenv('DB_HOST', 'db')}/{os.getenv('DB_NAME', 'pemex_db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # pool_pre_ping verifica que la conexion a MySQL siga activa antes de cada consulta
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}

    # URL interna del microservicio Gotenberg encargado de convertir documentos Word (.docx) a PDF
    GOTENBERG_URL = os.getenv('GOTENBERG_URL', 'http://gotenberg:3000')

    # Limite de tamano de cualquier peticion HTTP (archivos subidos). Evita denegacion de servicio (DoS) por archivos enormes.
    MAX_CONTENT_LENGTH = _int_env('MAX_UPLOAD_MB', 25) * 1024 * 1024

    # Tiempo de vida del token JWT en horas
    JWT_EXPIRATION_HOURS = _int_env('JWT_EXPIRATION_HOURS', 1)

    # Origenes permitidos para CORS, separados por coma. '*' mantiene compatibilidad en desarrollo.
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Contrasena inicial del usuario admin (solo se usa si el usuario aun no existe en la BD).
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')
