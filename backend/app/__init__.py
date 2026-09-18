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

        try:
            db.session.execute(text('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            '''))
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Crear el usuario admin por defecto si no existe
        try:
            from .models.user import User
            from werkzeug.security import generate_password_hash
            if not User.query.filter_by(username='admin').first():
                hashed = generate_password_hash('admin')
                user = User(username='admin', password_hash=hashed)
                db.session.add(user)
                db.session.commit()
                app.logger.info("Usuario 'admin' creado automáticamente.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error al crear usuario admin: {e}")
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Register routes
    register_routes(app)
    
    return app
