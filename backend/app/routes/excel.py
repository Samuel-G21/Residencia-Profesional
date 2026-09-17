from flask import Blueprint
from ..controllers.excel_controller import upload_excel

excel_bp = Blueprint('excel', __name__)
excel_bp.route('/upload-excel', methods=['POST'])(upload_excel)
