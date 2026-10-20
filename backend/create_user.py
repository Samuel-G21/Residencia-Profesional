"""
Script auxiliar para crear o restablecer manualmente el usuario administrador por defecto.

Guia para practicantes:
- Aunque el usuario 'admin' se crea automaticamente al iniciar la aplicacion en `app/__init__.py`,
  este script permite verificar o inicializar la cuenta desde la terminal ejecutando:
  `python create_user.py`
"""
from app import create_app
from app.models import db
from app.models.user import User
from werkzeug.security import generate_password_hash

# Inicializa el contexto de la aplicacion para poder interactuar con la base de datos via SQLAlchemy
app = create_app()
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        # Se almacena unicamente el hash seguro de la contrasena, nunca el texto plano
        hashed = generate_password_hash('admin')
        user = User(username='admin', password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        print("Admin user created")
    else:
        print("Admin user already exists")
