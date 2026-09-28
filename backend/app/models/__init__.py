from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from .course import Curso
from .history import HistorialCapacitacion
from .user import User
from .curp import Curp
