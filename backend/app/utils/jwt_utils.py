"""
Utilidades para emision y decodificacion de JSON Web Tokens (JWT).

Guia para practicantes:
- Cuando un usuario inicia sesion en `/api/auth/login`, se emite un token firmado con HS256
  mediante `generate_token(username)`.
- El frontend almacena ese token en `sessionStorage` y lo envia en la cabecera
  `Authorization: Bearer <token>` en cada peticion subsecuente.
"""
import datetime
import jwt
from flask import current_app


class TokenError(Exception):
    """Token ausente, invalido o expirado. El mensaje es apto para mostrarse al cliente."""


def _secret():
    """Obtiene la llave secreta configurada en la aplicacion Flask."""
    secret = current_app.config.get('SECRET_KEY')
    if not secret:
        raise RuntimeError("SECRET_KEY no configurada")
    return secret


def generate_token(username):
    """Genera un token JWT firmado con tiempo de expiracion configurable (por defecto 1 hora)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    hours = current_app.config.get('JWT_EXPIRATION_HOURS', 1)
    payload = {
        'sub': str(username),
        'username': str(username),
        'iat': now,
        'exp': now + datetime.timedelta(hours=hours),
    }
    return jwt.encode(payload, _secret(), algorithm='HS256')


def decode_token(token):
    """Devuelve el payload decodificado o lanza TokenError si el token expiro o fue alterado."""
    try:
        return jwt.decode(token, _secret(), algorithms=['HS256'], options={'require': ['exp']})
    except jwt.ExpiredSignatureError:
        raise TokenError('Token expirado. Inicia sesion nuevamente.')
    except jwt.InvalidTokenError:
        raise TokenError('Token invalido.')
