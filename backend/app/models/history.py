"""
Modelo ORM para la tabla 'historial_capacitacion'.

Guia para practicantes:
Registra la participacion individual de cada trabajador dentro de un evento (`Curso`).
Almacena:
- `estado`: 'ACTIVO', 'BAJA' (desertor/inasistencia) o 'NO APTO' (reprobado).
- `calificacion`: Evaluacion numerica (escala 0 a 10, donde >= 8 se considera aprobado).
- `motivo_baja`: Justificacion registrada cuando un trabajador es dado de baja.
"""
from . import db
from datetime import datetime


class HistorialCapacitacion(db.Model):
    __tablename__ = 'historial_capacitacion'

    id = db.Column(db.Integer, primary_key=True)
    # Llave foranea hacia `cursos.id_evento` con borrado en cascada
    id_evento = db.Column(
        db.String(50),
        db.ForeignKey('cursos.id_evento', ondelete='CASCADE'),
        nullable=False
    )
    ficha_trabajador = db.Column(db.String(50), nullable=False)
    nombre_trabajador = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), default='ACTIVO')
    calificacion = db.Column(db.Numeric(5, 2), nullable=True)
    motivo_baja = db.Column(db.Text, nullable=True)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
