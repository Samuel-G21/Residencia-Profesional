from flask import Blueprint
from ..controllers.document_controller import generate_docs, download_docs, extract_pdf

doc_bp = Blueprint('document', __name__)
doc_bp.route('/generate-docs', methods=['POST'])(generate_docs)
doc_bp.route('/download-docs/<id_evento>', methods=['GET'])(download_docs)
doc_bp.route('/extract-pdf', methods=['POST'])(extract_pdf)
