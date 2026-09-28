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
        try:
            db.create_all()
            app.logger.info("Tablas sincronizadas con SQLAlchemy.")
        except Exception as e:
            app.logger.error(f"Error sincronizando tablas: {e}")

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
