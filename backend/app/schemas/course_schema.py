from marshmallow import Schema, fields

class CursoSchema(Schema):
    id = fields.Int(dump_only=True)
    id_evento = fields.Str(required=True)
    nombre_evento = fields.Str(required=True)
    fase_actual = fields.Int()
    fecha_registro = fields.DateTime(dump_only=True)
    estado = fields.Str()
