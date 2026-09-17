import os
import shutil

base_dir = r"C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE\backend"
app_dir = os.path.join(base_dir, "app")

with open(os.path.join(app_dir, "routes", "init_routes.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Blueprint
from .health import health_bp
from .excel import excel_bp
from .document import doc_bp
from .stats import stats_bp
from .catalog import catalog_bp
from .event import event_bp

def register_routes(app):
    app.register_blueprint(health_bp, url_prefix='/')
    app.register_blueprint(excel_bp, url_prefix='/api')
    app.register_blueprint(doc_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')
    app.register_blueprint(catalog_bp, url_prefix='/api')
    app.register_blueprint(event_bp, url_prefix='/api')
""")

with open(os.path.join(app_dir, "routes", "health.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Sistema PEMEX Activo"}), 200
""")

with open(os.path.join(app_dir, "routes", "excel.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Blueprint
from ..controllers.excel_controller import upload_excel

excel_bp = Blueprint('excel', __name__)
excel_bp.route('/upload-excel', methods=['POST'])(upload_excel)
""")

with open(os.path.join(app_dir, "routes", "document.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Blueprint
from ..controllers.document_controller import generate_docs, download_docs, extract_pdf

doc_bp = Blueprint('document', __name__)
doc_bp.route('/generate-docs', methods=['POST'])(generate_docs)
doc_bp.route('/download-docs/<id_evento>', methods=['GET'])(download_docs)
doc_bp.route('/extract-pdf', methods=['POST'])(extract_pdf)
""")

with open(os.path.join(app_dir, "routes", "stats.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Blueprint
from ..controllers.stats_controller import get_stats

stats_bp = Blueprint('stats', __name__)
stats_bp.route('/stats', methods=['GET'])(get_stats)
""")

with open(os.path.join(app_dir, "routes", "catalog.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Blueprint
from ..controllers.catalog_controller import update_catalog

catalog_bp = Blueprint('catalog', __name__)
catalog_bp.route('/update-catalog', methods=['POST'])(update_catalog)
""")

with open(os.path.join(app_dir, "routes", "event.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Blueprint
from ..controllers.event_controller import (
    get_all_cursos, get_evento_fase, get_evento_trabajadores,
    update_evento_fase, delete_evento, cancelar_evento,
    baja_trabajador, upload_scpm07
)

event_bp = Blueprint('event', __name__)
event_bp.route('/cursos', methods=['GET'])(get_all_cursos)
event_bp.route('/evento/<id_evento>', methods=['GET'])(get_evento_fase)
event_bp.route('/evento/<id_evento>/trabajadores', methods=['GET'])(get_evento_trabajadores)
event_bp.route('/evento/<id_evento>/fase', methods=['PUT'])(update_evento_fase)
event_bp.route('/evento/<id_evento>', methods=['DELETE'])(delete_evento)
event_bp.route('/evento/<id_evento>/cancelar', methods=['PUT'])(cancelar_evento)
event_bp.route('/evento/<id_evento>/trabajador/<ficha>/baja', methods=['PUT'])(baja_trabajador)
event_bp.route('/evento/<id_evento>/scpm07', methods=['POST'])(upload_scpm07)
""")

print("Routes created successfully.")
