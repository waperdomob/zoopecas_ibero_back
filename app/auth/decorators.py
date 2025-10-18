from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.user import User

def role_required(*allowed_roles):
    """Decorador para verificar roles de usuario"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.activo:
                return jsonify({'message': 'Usuario inactivo o no encontrado'}), 403
            
            if not current_user.has_permission(allowed_roles):
                return jsonify({'message': 'Permisos insuficientes'}), 403
            
            return f(current_user=current_user, *args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Obtener el usuario actual desde el token JWT"""
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id) if current_user_id else None