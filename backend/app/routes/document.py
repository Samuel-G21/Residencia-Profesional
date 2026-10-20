"""
Rutas para extraccion de listas de asistencia (PDF), generacion de documentos (.docx/.xlsx),
descarga de expedientes (.zip) y carga de nuevas plantillas.
"""
from flask import Blueprint
from ..controllers.document_controller import generate_docs, download_docs, extract_pdf
from ..controllers.template_controller import upload_template

doc_bp = Blueprint('document', __name__)

# POST /api/generate-docs -> Pobla las plantillas individuales y grupales para un evento
doc_bp.route('/generate-docs', methods=['POST'])(generate_docs)

# GET /api/download-docs/<id_evento> -> Convierte a PDF via Gotenberg y empaqueta el expediente en ZIP
doc_bp.route('/download-docs/<id_evento>', methods=['GET'])(download_docs)

# POST /api/extract-pdf -> Extrae tabla de asistencia del formato SCPM-01 en PDF hacia un archivo Excel
doc_bp.route('/extract-pdf', methods=['POST'])(extract_pdf)

# POST /api/upload-template -> Procesa etiquetas [CAMPO] a sintaxis Jinja {{ campo }} y guarda la plantilla
doc_bp.route('/upload-template', methods=['POST'])(upload_template)
