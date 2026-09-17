from marshmallow import Schema, fields

class HistorialCapacitacionSchema(Schema):
    id = fields.Int(dump_only=True)
    id_evento = fields.Str(required=True)
    ficha_trabajador = fields.Str(required=True)
    nombre_trabajador = fields.Str(required=True)
    estado = fields.Str()
    calificacion = fields.Float()
    fecha_registro = fields.DateTime(dump_only=True)
