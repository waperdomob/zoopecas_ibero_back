from flask import request, jsonify
from flask_jwt_extended import jwt_required
import traceback

from app.api.pets import bp
from app.models.pet import Mascota
from app.models.medical import HistoriaClinica
from app.schemas.pet_schemas import MascotaSchema, MascotaUpdateSchema
from app.extensions import db
from app.utils.pagination import paginate_query
from app.utils.responses import success_response, error_response
from marshmallow import ValidationError

mascota_schema = MascotaSchema()
mascotas_schema = MascotaSchema(many=True)
mascota_update_schema = MascotaUpdateSchema()

@bp.route('', methods=['POST'])
@jwt_required()
def create_mascota():
    """Crear nueva mascota"""
    try:
        data = request.get_json()
        validated_data = mascota_schema.load(data)
        
        mascota = Mascota(**validated_data)
        mascota.save()
        
        # Crear historia clínica automáticamente
        historia = HistoriaClinica(
            mascota_id=mascota.mascota_id,
            peso_inicial=mascota.peso_actual
        )
        historia.save()
        
        return success_response(
            'Mascota creada exitosamente',
            mascota.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear mascota', str(e), 500)

@bp.route('', methods=['GET'])
@jwt_required()
def list_mascotas():
    """Listar mascotas con paginación y filtros"""
    try:
        search = request.args.get('search', '')
        cliente_id = request.args.get('cliente_id', type=int)
        especie = request.args.get('especie', '')
        activo = request.args.get('activo', type=lambda x: x.lower() == 'true')
        
        query = Mascota.query
        
        if search:
            query = Mascota.search(search)
        
        if cliente_id:
            query = query.filter_by(cliente_id=cliente_id)
        
        if especie:
            query = query.filter_by(especie=especie)
        
        if activo is not None:
            query = query.filter_by(activo=activo)
        
        query = query.order_by(Mascota.fecha_registro.desc())
        
        pagination = paginate_query(query)
        
        return success_response(
            'Mascotas obtenidas exitosamente',
            {
                'mascotas': [m.to_dict() for m in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        print(traceback.print_exc())
        return error_response('Error al obtener mascotas', str(e), 500)

@bp.route('/<int:mascota_id>', methods=['GET'])
@jwt_required()
def get_mascota(mascota_id):
    """Obtener mascota por ID"""
    try:
        mascota = Mascota.query.get_or_404(mascota_id)
        
        return success_response(
            'Mascota obtenida exitosamente',
            mascota.to_dict()
        )
        
    except Exception as e:
        return error_response('Mascota no encontrada', str(e), 404)

@bp.route('/<int:mascota_id>', methods=['PUT'])
@jwt_required()
def update_mascota(mascota_id):
    """Actualizar mascota"""
    try:
        mascota = Mascota.query.get_or_404(mascota_id)
        data = request.get_json()
        
        validated_data = mascota_update_schema.load(data)
        mascota.update(**validated_data)
        
        return success_response(
            'Mascota actualizada exitosamente',
            mascota.to_dict()
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al actualizar mascota', str(e), 500)

@bp.route('/<int:mascota_id>', methods=['DELETE'])
@jwt_required()
def delete_mascota(mascota_id):
    """Desactivar mascota"""
    try:
        mascota = Mascota.query.get_or_404(mascota_id)
        mascota.update(activo=False)
        
        return success_response('Mascota desactivada exitosamente')
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al desactivar mascota', str(e), 500)