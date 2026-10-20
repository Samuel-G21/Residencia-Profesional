"""
Controlador de Autenticacion y Gestion de Usuarios (`/api/auth`).

Guia para practicantes:
- Implementa inicio de sesion (`/api/auth/login`) validando credenciales contra MySQL y
  devolviendo un token JWT.
- Incluye proteccion contra ataques de fuerza bruta (bloqueo temporal tras 5 intentos fallidos)
  y mitigacion de ataques de temporizacion (timing attacks) mediante `_DUMMY_HASH`.
- El registro de nuevos usuarios (`/api/auth/register`) esta protegido por el middleware JWT
  en `init_routes.py`, por lo que solo un usuario ya autenticado puede dar de alta a otro.
"""
import time
import threading
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from ..models import db
from ..models.user import User
from ..utils.jwt_utils import generate_token
from ..utils.security import error_response

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

MAX_USERNAME_LEN = 50
MAX_PASSWORD_LEN = 128
MIN_NEW_PASSWORD_LEN = 8

# Hash senuelo: se verifica aunque el usuario no exista para no revelar,
# por diferencia de tiempo de respuesta, que nombres de usuario son validos.
_DUMMY_HASH = generate_password_hash('dummy-password-for-timing')

# Limitador simple de intentos fallidos (por IP + usuario). Es en memoria por proceso:
# con N workers de Gunicorn el limite efectivo es N veces mayor, pero frena ataques de fuerza bruta.
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_SECONDS = 15 * 60
_failed_attempts = {}
_failed_lock = threading.Lock()


def _attempt_key(username):
    """Genera una clave unica combinando la IP del cliente y el nombre de usuario en minusculas."""
    return f"{request.remote_addr}|{username.lower()}"


def _is_locked(key):
    """Verifica si la combinacion IP+usuario ha superado el limite de intentos fallidos recientes."""
    now = time.time()
    with _failed_lock:
        attempts = [t for t in _failed_attempts.get(key, []) if now - t < _LOCKOUT_SECONDS]
        if attempts:
            _failed_attempts[key] = attempts
        else:
            _failed_attempts.pop(key, None)
        return len(attempts) >= _MAX_FAILED_ATTEMPTS


def _register_failure(key):
    """Registra la marca de tiempo de un intento de inicio de sesion fallido."""
    with _failed_lock:
        if len(_failed_attempts) > 10000:
            _failed_attempts.clear()
        _failed_attempts.setdefault(key, []).append(time.time())


def _clear_failures(key):
    """Limpia el historial de intentos fallidos tras un inicio de sesion exitoso."""
    with _failed_lock:
        _failed_attempts.pop(key, None)


def _read_credentials():
    """Extrae, limpia y valida el formato de `username` y `password` desde el cuerpo JSON."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, None
    username = data.get('username')
    password = data.get('password')
    if not isinstance(username, str) or not isinstance(password, str):
        return None, None
    username = username.strip()
    if not username or not password:
        return None, None
    if len(username) > MAX_USERNAME_LEN or len(password) > MAX_PASSWORD_LEN:
        return None, None
    return username, password


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica a un usuario y devuelve un token JWT si las credenciales son correctas."""
    username, password = _read_credentials()
    if not username:
        return jsonify({"status": "error", "message": "Usuario o contraseña faltante o inválido"}), 400

    key = _attempt_key(username)
    if _is_locked(key):
        return jsonify({"status": "error", "message": "Demasiados intentos fallidos. Intenta de nuevo más tarde."}), 429

    user = User.query.filter_by(username=username).first()
    password_ok = check_password_hash(user.password_hash if user else _DUMMY_HASH, password)

    if user and password_ok:
        _clear_failures(key)
        token = generate_token(user.username)
        return jsonify({
            "status": "success",
            "message": "Login exitoso",
            "username": user.username,
            "token": token
        }), 200

    _register_failure(key)
    return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registra un nuevo usuario en la base de datos.
    Este endpoint requiere un token JWT valido (ver `init_routes.check_token`).
    """
    username, password = _read_credentials()
    if not username:
        return jsonify({"status": "error", "message": "Usuario o contraseña faltante o inválido"}), 400
    if len(password) < MIN_NEW_PASSWORD_LEN:
        return jsonify({
            "status": "error",
            "message": f"La contraseña debe tener al menos {MIN_NEW_PASSWORD_LEN} caracteres"
        }), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 400

    new_user = User(username=username, password_hash=generate_password_hash(password))
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success", "message": "Usuario creado exitosamente"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 400
    except Exception as e:
        db.session.rollback()
        return error_response("No se pudo crear el usuario", 500, e)
