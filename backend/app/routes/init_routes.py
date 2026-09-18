from flask import Blueprint, request, jsonify, current_app
from .health import health_bp
from .excel import excel_bp
from .document import doc_bp
from .stats import stats_bp
from .catalog import catalog_bp
from .event import event_bp
from ..controllers.auth_controller import auth_bp
import jwt

def register_routes(app):
    app.register_blueprint(health_bp, url_prefix='/')
    app.register_blueprint(excel_bp, url_prefix='/api')
    app.register_blueprint(doc_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')
    app.register_blueprint(catalog_bp, url_prefix='/api')
    app.register_blueprint(event_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)

    @app.before_request
    def check_token():
        if request.method == 'OPTIONS':
            return
        path = request.path
        if path.startswith('/api/') and not path.startswith('/api/auth/'):
            token = None
            if 'Authorization' in request.headers:
                parts = request.headers['Authorization'].split()
                if len(parts) == 2 and parts[0] == 'Bearer':
                    token = parts[1]
            if not token:
                return jsonify({'status': 'error', 'message': 'Token is missing!'}), 401
            try:
                jwt.decode(token, current_app.config.get('SECRET_KEY', 'default-secret-key'), algorithms=['HS256'])
            except Exception as e:
                return jsonify({'status': 'error', 'message': 'Token is invalid!', 'error': str(e)}), 401
