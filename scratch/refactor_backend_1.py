import os

base_dir = r"C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE\backend"
app_dir = os.path.join(base_dir, "app")

dirs = [
    "models",
    "routes",
    "controllers",
    "services",
    "utils",
    "schemas"
]

for d in dirs:
    os.makedirs(os.path.join(app_dir, d), exist_ok=True)

# create __init__.py files
for d in dirs:
    with open(os.path.join(app_dir, d, "__init__.py"), "w") as f:
        f.write("")

with open(os.path.join(app_dir, "__init__.py"), "w", encoding='utf-8') as f:
    f.write("""from flask import Flask
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
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Register routes
    register_routes(app)
    
    return app
""")

with open(os.path.join(app_dir, "config.py"), "w", encoding='utf-8') as f:
    f.write("""import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER', 'pemex_user')}:{os.getenv('DB_PASSWORD', 'pemex_password')}@{os.getenv('DB_HOST', 'db')}/{os.getenv('DB_NAME', 'pemex_db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOTENBERG_URL = os.getenv('GOTENBERG_URL', 'http://gotenberg:3000')
""")

with open(os.path.join(app_dir, "models", "__init__.py"), "w", encoding='utf-8') as f:
    f.write("""from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from .course import Curso
from .history import HistorialCapacitacion
""")

with open(os.path.join(app_dir, "models", "course.py"), "w", encoding='utf-8') as f:
    f.write("""from . import db
from datetime import datetime

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    id_evento = db.Column(db.String(50), unique=True, nullable=False)
    nombre_evento = db.Column(db.String(255), nullable=False)
    fase_actual = db.Column(db.Integer, default=1)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='ACTIVO')
    
    historial = db.relationship('HistorialCapacitacion', backref='curso', lazy=True, cascade="all, delete-orphan")
""")

with open(os.path.join(app_dir, "models", "history.py"), "w", encoding='utf-8') as f:
    f.write("""from . import db
from datetime import datetime

class HistorialCapacitacion(db.Model):
    __tablename__ = 'historial_capacitacion'
    id = db.Column(db.Integer, primary_key=True)
    id_evento = db.Column(db.String(50), db.ForeignKey('cursos.id_evento', ondelete='CASCADE'), nullable=False)
    ficha_trabajador = db.Column(db.String(50), nullable=False)
    nombre_trabajador = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), default='ACTIVO')
    calificacion = db.Column(db.Numeric(5,2), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
""")

with open(os.path.join(app_dir, "schemas", "course_schema.py"), "w", encoding='utf-8') as f:
    f.write("""from marshmallow import Schema, fields

class CursoSchema(Schema):
    id = fields.Int(dump_only=True)
    id_evento = fields.Str(required=True)
    nombre_evento = fields.Str(required=True)
    fase_actual = fields.Int()
    fecha_registro = fields.DateTime(dump_only=True)
    estado = fields.Str()
""")

with open(os.path.join(app_dir, "schemas", "history_schema.py"), "w", encoding='utf-8') as f:
    f.write("""from marshmallow import Schema, fields

class HistorialCapacitacionSchema(Schema):
    id = fields.Int(dump_only=True)
    id_evento = fields.Str(required=True)
    ficha_trabajador = fields.Str(required=True)
    nombre_trabajador = fields.Str(required=True)
    estado = fields.Str()
    calificacion = fields.Float()
    fecha_registro = fields.DateTime(dump_only=True)
""")

print("Backend models and config created successfully.")
