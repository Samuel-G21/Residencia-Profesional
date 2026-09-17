from flask import Flask
from flask_cors import CORS
from .config import Config
from .models import db
from .routes.init_routes import register_routes
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    # Init extensions
    db.init_app(app)
    
    with app.app_context():
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE cursos ADD COLUMN tipo_curso VARCHAR(50) DEFAULT 'Actualización'"))
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        try:
            db.session.execute(text("ALTER TABLE historial_capacitacion ADD COLUMN motivo_baja TEXT"))
            db.session.commit()
        except Exception:
            db.session.rollback()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Register routes
    register_routes(app)
    
    return app
