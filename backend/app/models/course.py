"""
Modelo ORM para la tabla 'cursos'.

Guia para practicantes:
Representa un evento o curso de capacitacion registrado en el sistema (identificado por su
clave de evento SIRHN). Su ciclo de vida avanza por 5 fases:
  1: Registro / Programacion
  2: Ejecucion del Evento
  3: Extraccion SCPM-01
  4: Integracion de Expediente
  5: Cierre / Firmas
Los estados posibles del curso son: 'ACTIVO', 'FINALIZADO' o 'CANCELADO'.
"""
from . import db
from datetime import datetime


class Curso(db.Model):
    __tablename__ = 'cursos'

    # Clave unica del evento en SIRHN (ej. '50698401')
    id_evento = db.Column(db.String(50), primary_key=True, nullable=False)
    nombre_evento = db.Column(db.String(255), nullable=False)
    fase_actual = db.Column(db.Integer, default=1)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='ACTIVO')
    # Tipo de curso: 'Actualizacion' o 'Ascenso' (determina si se genera SCPM-05 o SCPM-05A)
    tipo_curso = db.Column(db.String(50), nullable=True)

    # Relacion uno-a-muchos con los trabajadores inscritos; al eliminar un curso se elimina su historial
    historial = db.relationship(
        'HistorialCapacitacion',
        backref='curso',
        lazy=True,
        cascade="all, delete-orphan"
    )
