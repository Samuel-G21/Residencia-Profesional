from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db
from ..models.user import User
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config.get('SECRET_KEY', 'default-secret-key'), algorithm='HS256')
        
        return jsonify({"status": "success", "message": "Login exitoso", "username": username, "token": token}), 200
    else:
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    # Solo para inicializar usuarios (debería estar protegido en producción)
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success", "message": "Usuario creado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
