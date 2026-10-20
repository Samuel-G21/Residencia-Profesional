"""
Registro centralizado de Blueprints y middleware de autenticacion JWT.

Guia para practicantes:
- Todos los modulos de rutas se registran aqui bajo el prefijo `/api` (excepto `health_bp` en `/`).
- La funcion `check_token()` se ejecuta automaticamente antes de cada peticion (`@app.before_request`)
  y protege todos los endpoints bajo `/api/*` salvo `/api/auth/login`.
"""
from flask import request, jsonify, current_app
from .health import health_bp
from .excel import excel_bp
from .document import doc_bp
from .stats import stats_bp
from .catalog import catalog_bp
from .event import event_bp
from .stps import stps_bp
from ..controllers.auth_controller import auth_bp
import jwt


def register_routes(app):
    """Registra todos los Blueprints en la instancia principal de Flask y configura el filtro JWT."""
    app.register_blueprint(health_bp, url_prefix='/')
    app.register_blueprint(excel_bp, url_prefix='/api')
    app.register_blueprint(doc_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')
    app.register_blueprint(catalog_bp, url_prefix='/api')
    app.register_blueprint(event_bp, url_prefix='/api')
    app.register_blueprint(stps_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)

    @app.before_request
    def check_token():
        """
        Middleware global de seguridad:
        Verifica que toda peticion dirigida a `/api/` (excepto login y preflight OPTIONS)
        incluya un token JWT valido en el encabezado `Authorization: Bearer <token>`.
        """
        if request.method == 'OPTIONS':
            return
        path = request.path
        if path.startswith('/api/') and not path.startswith('/api/auth/login'):
            token = None
            if 'Authorization' in request.headers:
                parts = request.headers['Authorization'].split()
                if len(parts) == 2 and parts[0] == 'Bearer':
                    token = parts[1]
            if not token:
                return jsonify({'status': 'error', 'message': 'Token is missing!'}), 401
            try:
                jwt.decode(
                    token,
                    current_app.config.get('SECRET_KEY', 'default-secret-key'),
                    algorithms=['HS256']
                )
            except Exception:
                return jsonify({'status': 'error', 'message': 'Token is invalid!'}), 401
