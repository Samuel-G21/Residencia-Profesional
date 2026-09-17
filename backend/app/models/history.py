from . import db
from datetime import datetime

class HistorialCapacitacion(db.Model):
    __tablename__ = 'historial_capacitacion'
    id = db.Column(db.Integer, primary_key=True)
    id_evento = db.Column(db.String(50), db.ForeignKey('cursos.id_evento', ondelete='CASCADE'), nullable=False)
    ficha_trabajador = db.Column(db.String(50), nullable=False)
    nombre_trabajador = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), default='ACTIVO')
    calificacion = db.Column(db.Numeric(5,2), nullable=True)
    motivo_baja = db.Column(db.Text, nullable=True)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
