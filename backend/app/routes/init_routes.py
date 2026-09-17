from flask import Blueprint
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
