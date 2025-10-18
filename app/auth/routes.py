from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.auth import bp
from app.auth.utils import validate_user_data
from app.auth.decorators import get_current_user, role_required
from app.models.user import User, UserRole
from app.extensions import db
from datetime import datetime

@bp.route('/register', methods=['POST'])
def register():
    """Registro de nuevos usuarios"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = validate_user_data(data)
        if errors:
            return jsonify({'message': 'Errores de validación', 'errors': errors}), 400
        
        # Crear usuario
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            telefono=data.get('telefono'),
            rol=UserRole(data.get('rol', 'asistente'))
        )
        
        user.save()
        
        # Generar tokens
        tokens = user.generate_tokens()
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'data': tokens
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Inicio de sesión"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username y password son requeridos'}), 400
        
        # Buscar usuario por username o email
        user = User.find_by_username(data['username']) or User.find_by_email(data['username'])
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Credenciales inválidas'}), 401
        
        if not user.activo:
            return jsonify({'message': 'Usuario inactivo'}), 401
        
        # Actualizar último acceso
        user.update(ultimo_acceso=datetime.utcnow())
        
        # Generar tokens
        tokens = user.generate_tokens()
        
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'data': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar token de acceso"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.activo:
            return jsonify({'message': 'Usuario no válido'}), 401
        
        # Generar nuevo token de acceso
        additional_claims = {
            "rol": user.rol,
            "nombre_completo": f"{user.nombre} {user.apellidos}"
        }
        
        new_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        
        return jsonify({
            'message': 'Token renovado exitosamente',
            'access_token': new_token
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtener perfil del usuario actual"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'message': 'Perfil obtenido exitosamente',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nombre': user.nombre,
                'apellidos': user.apellidos,
                'telefono': user.telefono,
                'rol': user.rol,
                'ultimo_acceso': user.ultimo_acceso.isoformat() if user.ultimo_acceso else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        # Validar datos (excluyendo username y email si no se proporcionan)
        errors = validate_user_data(data, is_update=True)
        if errors:
            return jsonify({'message': 'Errores de validación', 'errors': errors}), 400
        
        # Actualizar campos permitidos
        allowed_fields = ['nombre', 'apellidos', 'telefono']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if update_data:
            user.update(**update_data)
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nombre': user.nombre,
                'apellidos': user.apellidos,
                'telefono': user.telefono,
                'rol': user.rol
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@bp.route('/users', methods=['GET'])
@role_required('admin')
def list_users(current_user):
    """Listar usuarios (solo admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'message': 'Usuarios obtenidos exitosamente',
            'data': {
                'users': [{
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'nombre': user.nombre,
                    'apellidos': user.apellidos,
                    'rol': user.rol,
                    'activo': user.activo,
                    'fecha_creacion': user.fecha_creacion
                } for user in users.items],
                'pagination': {
                    'page': page,
                    'pages': users.pages,
                    'per_page': per_page,
                    'total': users.total
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500
