from . import db
from datetime import datetime

class Curso(db.Model):
    __tablename__ = 'cursos'
    id_evento = db.Column(db.String(50), primary_key=True, nullable=False)
    nombre_evento = db.Column(db.String(255), nullable=False)
    fase_actual = db.Column(db.Integer, default=1)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='ACTIVO')
    tipo_curso = db.Column(db.String(50), nullable=True)
    
    historial = db.relationship('HistorialCapacitacion', backref='curso', lazy=True, cascade="all, delete-orphan")
