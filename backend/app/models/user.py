"""
Modelo ORM para la tabla 'usuarios'.

Guia para practicantes:
Gestiona las cuentas con acceso administrativo a la plataforma web.
Por seguridad, nunca se guarda la contrasena en texto plano, sino el hash generado
mediante `werkzeug.security.generate_password_hash`.
"""
from . import db


class User(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
