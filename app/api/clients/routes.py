from flask import request, jsonify
from flask_jwt_extended import jwt_required
import traceback

from app.api.clients import bp
from app.models.client import Cliente
from app.schemas.client_schemas import ClienteSchema, ClienteUpdateSchema
from app.extensions import db
from app.utils.pagination import paginate_query
from app.utils.responses import success_response, error_response
from app.auth.decorators import role_required
from marshmallow import ValidationError

cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)
cliente_update_schema = ClienteUpdateSchema()

@bp.route('', methods=['POST'])
@jwt_required()
def create_cliente():
    """Crear nuevo cliente"""
    try:
        data = request.get_json()
        validated_data = cliente_schema.load(data)
        
        cliente = Cliente(**validated_data)
        cliente.save()
        
        return success_response(
            'Cliente creado exitosamente',
            cliente.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear cliente', str(e), 500)

@bp.route('', methods=['GET'])
@jwt_required()
def list_clientes():
    """Listar clientes con paginación y búsqueda"""
    try:
        search = request.args.get('search', '')
        activo = request.args.get('activo', type=lambda x: x.lower() == 'true')
        
        query = Cliente.query
        
        if search:
            query = Cliente.search(search)
        
        if activo is not None:
            query = query.filter_by(activo=activo)
        
        query = query.order_by(Cliente.fecha_registro.desc())
        
        pagination = paginate_query(query)
        
        return success_response(
            'Clientes obtenidos exitosamente',
            {
                'clientes': [c.to_dict() for c in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        print(traceback.format_exc())
        return error_response('Error al obtener clientes', str(e), 500)

@bp.route('/<int:cliente_id>', methods=['GET'])
@jwt_required()
def get_cliente(cliente_id):
    """Obtener cliente por ID"""
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        include_mascotas = request.args.get('include_mascotas', 'false').lower() == 'true'
        
        return success_response(
            'Cliente obtenido exitosamente',
            cliente.to_dict(include_mascotas=include_mascotas)
        )
        
    except Exception as e:
        return error_response('Cliente no encontrado', str(e), 404)

@bp.route('/<int:cliente_id>', methods=['PUT'])
@jwt_required()
def update_cliente(cliente_id):
    """Actualizar cliente"""
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        data = request.get_json()
        
        validated_data = cliente_update_schema.load(data)
        cliente.update(**validated_data)
        
        return success_response(
            'Cliente actualizado exitosamente',
            cliente.to_dict()
        )
        
    except ValidationError as e:
        print(traceback.format_exc())
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        print(traceback.format_exc())
        db.session.rollback()
        return error_response('Error al actualizar cliente', str(e), 500)

@bp.route('/<int:cliente_id>', methods=['DELETE'])
@role_required('Administrador')
def delete_cliente(cliente_id, current_user):
    """Eliminar cliente (solo admin)"""
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        if cliente.mascotas.filter_by(activo=True).count() > 0:
            return error_response(
                'No se puede eliminar el cliente porque tiene mascotas activas',
                None,
                400
            )
        
        cliente.delete()
        
        return success_response('Cliente eliminado exitosamente')
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al eliminar cliente', str(e), 500)

@bp.route('/<int:cliente_id>/mascotas', methods=['GET'])
@jwt_required()
def get_cliente_mascotas(cliente_id):
    """Obtener mascotas de un cliente"""
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        mascotas = cliente.mascotas.filter_by(activo=True).all()
        
        return success_response(
            'Mascotas obtenidas exitosamente',
            [m.to_dict() for m in mascotas]
        )
        
    except Exception as e:
        return error_response('Error al obtener mascotas', str(e), 500)

@bp.route('/documento/<documento>', methods=['GET'])
@jwt_required()
def get_cliente_by_documento(documento):
    """Buscar cliente por documento"""
    try:
        cliente = Cliente.find_by_documento(documento)
        
        if not cliente:
            return error_response('Cliente no encontrado', None, 404)
        
        return success_response(
            'Cliente encontrado',
            cliente.to_dict(include_mascotas=True)
        )
        
    except Exception as e:
        return error_response('Error al buscar cliente', str(e), 500)