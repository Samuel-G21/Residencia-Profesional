"""
Ruta de verificacion de salud (Health Check) del servidor Backend.
Utilizada por pruebas automatizadas (Pytest) y monitoreo de contenedores.
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/', methods=['GET'])
def health_check():
    """Confirma que la API de Flask se encuentra en ejecucion."""
    return jsonify({"status": "success", "message": "Sistema PEMEX Activo"}), 200
