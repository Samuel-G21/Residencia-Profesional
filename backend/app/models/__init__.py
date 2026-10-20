"""
Inicializacion del ORM SQLAlchemy y exportacion centralizada de modelos.

Guia para practicantes:
Importar todos los modelos aqui asegura que `db.create_all()` (en `app/__init__.py`)
detecte todas las tablas y las cree automaticamente al arrancar el servidor.
"""
from flask_sqlalchemy import SQLAlchemy

# Instancia compartida de SQLAlchemy vinculada a Flask en create_app()
db = SQLAlchemy()

# Importacion de modelos para registrarlos en el metadata de SQLAlchemy
from .course import Curso
from .history import HistorialCapacitacion
from .user import User
from .curp import Curp
