"""
Modelo ORM para la tabla 'curps' (Catalogo Maestro de CURP).

Guia para practicantes:
Permite cruzar la ficha de cada trabajador contra su CURP oficial al generar
constancias (como DC-3 y SIRCE) y calcular estadisticas demograficas por genero
(usando el caracter en la posicion 11 de la CURP: 'H' = Hombre, 'M' = Mujer).
Se alimenta desde el modulo de Administracion de Catalogos subiendo `CURP.xlsx`.
"""
from . import db


class Curp(db.Model):
    __tablename__ = 'curps'

    # Numero de ficha institucional del trabajador
    ficha = db.Column(db.String(50), primary_key=True)
    # Clave Unica de Registro de Poblacion (18 caracteres)
    curp = db.Column(db.String(18), nullable=False)
