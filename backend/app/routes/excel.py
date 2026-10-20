"""
Rutas auxiliares para lectura previa de cursos desde un archivo Excel.
"""
from flask import Blueprint
from ..controllers.excel_controller import upload_excel

excel_bp = Blueprint('excel', __name__)

# POST /api/upload-excel -> Devuelve la lista unica de eventos (ID y NOMBRE DEL EVENTO) presentes en un Excel
excel_bp.route('/upload-excel', methods=['POST'])(upload_excel)
