"""
Esquema de validacion y serializacion para el modelo `Curso` usando Marshmallow.

Guia para practicantes:
Define la estructura esperada al serializar objetos `Curso` a JSON o validar datos de entrada.
"""
from marshmallow import Schema, fields


class CursoSchema(Schema):
    id = fields.Int(dump_only=True)
    id_evento = fields.Str(required=True)
    nombre_evento = fields.Str(required=True)
    fase_actual = fields.Int()
    fecha_registro = fields.DateTime(dump_only=True)
    estado = fields.Str()
