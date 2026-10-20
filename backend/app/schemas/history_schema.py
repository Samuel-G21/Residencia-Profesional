"""
Esquema de validacion y serializacion para el modelo `HistorialCapacitacion` usando Marshmallow.

Guia para practicantes:
Define los campos expuestos de cada registro de participacion de un trabajador en un curso.
"""
from marshmallow import Schema, fields


class HistorialCapacitacionSchema(Schema):
    id = fields.Int(dump_only=True)
    id_evento = fields.Str(required=True)
    ficha_trabajador = fields.Str(required=True)
    nombre_trabajador = fields.Str(required=True)
    estado = fields.Str()
    calificacion = fields.Float()
    fecha_registro = fields.DateTime(dump_only=True)
