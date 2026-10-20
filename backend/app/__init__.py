"""
Factoria de la aplicacion Flask (Application Factory Pattern).

Guia para practicantes:
Este modulo centraliza la creacion y configuracion del servidor backend:
1. Carga las variables de configuracion desde `config.py`.
2. Habilita CORS para permitir peticiones desde el frontend en React.
3. Inicializa el ORM SQLAlchemy y sincroniza automaticamente los modelos con MySQL.
4. Garantiza que exista el usuario administrador inicial ('admin').
5. Registra todos los Blueprints (rutas de la API) definidos en `app/routes/`.
"""
from flask import Flask
from flask_cors import CORS
from .config import Config
from .models import db
from .routes.init_routes import register_routes
import logging


def create_app():
    """Crea, configura y devuelve una instancia de la aplicacion Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Habilita el intercambio de recursos de origen cruzado (CORS) entre frontend y backend
    CORS(app)

    # Inicializa la conexion de SQLAlchemy con la aplicacion actual
    db.init_app(app)

    with app.app_context():
        # Crea las tablas en la base de datos si aun no existen (basado en los modelos de app/models/)
        try:
            db.create_all()
            app.logger.info("Tablas sincronizadas con SQLAlchemy.")
        except Exception as e:
            app.logger.error(f"Error sincronizando tablas: {e}")

        # Crear el usuario admin por defecto si no existe en la tabla 'usuarios'
        try:
            from .models.user import User
            from werkzeug.security import generate_password_hash
            if not User.query.filter_by(username='admin').first():
                hashed = generate_password_hash(app.config.get('ADMIN_PASSWORD', 'admin'))
                user = User(username='admin', password_hash=hashed)
                db.session.add(user)
                db.session.commit()
                app.logger.info("Usuario 'admin' creado automaticamente.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error al crear usuario admin: {e}")

    # Configuracion del formato estandar de logs para depuracion en contenedor
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Registra todos los endpoints REST y el middleware de autenticacion JWT
    register_routes(app)

    return app
