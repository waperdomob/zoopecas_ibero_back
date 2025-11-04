from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api.medical import bp
from app.models.medical import HistoriaClinica, Consulta, Veterinario, SeguimientoPaciente
from app.models.pet import Mascota
from app.schemas.medical_schemas import (
    HistoriaClinicaSchema, ConsultaSchema, SeguimientoSchema
)
from app.extensions import db
from app.utils.pagination import paginate_query
from app.utils.responses import success_response, error_response
from app.auth.decorators import role_required
from marshmallow import ValidationError

historia_schema = HistoriaClinicaSchema()
consulta_schema = ConsultaSchema()
seguimiento_schema = SeguimientoSchema()

@bp.route('/historias', methods=['GET'])
@jwt_required()
def list_historias():
    """Listar historias clínicas"""
    try:
        mascota_id = request.args.get('mascota_id', type=int)
        
        query = HistoriaClinica.query
        
        if mascota_id:
            query = query.filter_by(mascota_id=mascota_id)
        
        pagination = paginate_query(query)
        
        return success_response(
            'Historias clínicas obtenidas exitosamente',
            {
                'historias': [h.to_dict(include_consultas=True) for h in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        return error_response('Error al obtener historias', str(e), 500)

@bp.route('/historias/<int:historia_id>', methods=['GET'])
@jwt_required()
def get_historia(historia_id):
    """Obtener historia clínica por ID"""
    try:
        historia = HistoriaClinica.query.get_or_404(historia_id)
        
        return success_response(
            'Historia clínica obtenida exitosamente',
            historia.to_dict(include_consultas=True)
        )
        
    except Exception as e:
        return error_response('Historia clínica no encontrada', str(e), 404)

@bp.route('/historias/<int:historia_id>', methods=['PUT'])
@jwt_required()
def update_historia(historia_id):
    """Actualizar historia clínica"""
    try:
        historia = HistoriaClinica.query.get_or_404(historia_id)
        data = request.get_json()
        
        allowed_fields = [
            'caracteristicas_especiales', 'queja_principal', 'tratamientos_previos',
            'enfermedades_anteriores', 'cirugias_anteriores', 'tipo_dieta',
            'detalle_dieta', 'medicina_preventiva', 'observaciones_generales', 'activa'
        ]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        historia.update(**update_data)
        
        return success_response(
            'Historia clínica actualizada exitosamente',
            historia.to_dict()
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al actualizar historia', str(e), 500)

@bp.route('/consultas', methods=['POST'])
@role_required('Administrador', 'Veterinario')
def create_consulta(current_user):
    """Crear nueva consulta"""
    try:
        data = request.get_json()
        validated_data = consulta_schema.load(data)
        
        historia = HistoriaClinica.query.get(validated_data['historia_id'])
        if not historia:
            return error_response('Historia clínica no encontrada', None, 404)
        
        consulta = Consulta(**validated_data)
        consulta.save()
        
        # Actualizar peso de la mascota si se proporciona
        if consulta.peso:
            mascota = historia.paciente
            mascota.update(peso_actual=consulta.peso)
        
        return success_response(
            'Consulta creada exitosamente',
            consulta.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear consulta', str(e), 500)

@bp.route('/consultas', methods=['GET'])
@jwt_required()
def list_consultas():
    """Listar consultas con filtros"""
    try:
        historia_id = request.args.get('historia_id', type=int)
        mascota_id = request.args.get('mascota_id', type=int)
        veterinario_id = request.args.get('veterinario_id', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        query = Consulta.query
        
        if historia_id:
            query = query.filter_by(historia_id=historia_id)
        
        if mascota_id:
            query = query.join(HistoriaClinica).filter(HistoriaClinica.mascota_id == mascota_id)
        
        if veterinario_id:
            query = query.filter_by(veterinario_id=veterinario_id)
        
        if fecha_desde:
            query = query.filter(Consulta.fecha_consulta >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Consulta.fecha_consulta <= fecha_hasta)
        
        query = query.order_by(Consulta.fecha_consulta.desc(), Consulta.hora_consulta.desc())
        
        pagination = paginate_query(query)
        
        return success_response(
            'Consultas obtenidas exitosamente',
            {
                'consultas': [c.to_dict() for c in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        return error_response('Error al obtener consultas', str(e), 500)

@bp.route('/consultas/<int:consulta_id>', methods=['GET'])
@jwt_required()
def get_consulta(consulta_id):
    """Obtener consulta por ID"""
    try:
        consulta = Consulta.query.get_or_404(consulta_id)
        
        return success_response(
            'Consulta obtenida exitosamente',
            consulta.to_dict()
        )
        
    except Exception as e:
        return error_response('Consulta no encontrada', str(e), 404)

@bp.route('/consultas/<int:consulta_id>', methods=['PUT'])
@role_required('Administrador', 'Veterinario')
def update_consulta(consulta_id, current_user):
    """Actualizar consulta"""
    try:
        consulta = Consulta.query.get_or_404(consulta_id)
        data = request.get_json()
        
        # Validar permisos
        if current_user.rol != 'Administrador' and consulta.veterinario_id != current_user.usuario_id:
            return error_response('No tiene permisos para editar esta consulta', None, 403)
        
        allowed_fields = [
            'motivo_consulta', 'inspeccion_general', 'temperatura', 'pulso',
            'respiracion', 'tiempo_llenado_capilar', 'hidratacion', 'peso', 'ganglios',
            'sistema_digestivo', 'sistema_respiratorio', 'sistema_cardiovascular',
            'sistema_urinario', 'sistema_genital', 'sistema_nervioso', 'sistema_locomotor',
            'piel_anexos', 'hallazgos', 'examenes_solicitados', 'examenes_autorizados',
            'diagnostico', 'pronostico', 'tratamiento_ideal', 'tratamiento_instaurado',
            'cotizacion_tratamiento', 'observaciones', 'proxima_cita', 'costo_consulta'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        consulta.update(**update_data)
        
        return success_response(
            'Consulta actualizada exitosamente',
            consulta.to_dict()
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al actualizar consulta', str(e), 500)

@bp.route('/seguimientos', methods=['POST'])
@role_required('Administrador', 'Veterinario', 'Asistente')
def create_seguimiento(current_user):
    """Crear seguimiento de paciente"""
    try:
        data = request.get_json()
        validated_data = seguimiento_schema.load(data)
        
        seguimiento = SeguimientoPaciente(**validated_data)
        seguimiento.save()
        
        return success_response(
            'Seguimiento creado exitosamente',
            seguimiento.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear seguimiento', str(e), 500)

@bp.route('/seguimientos/<int:consulta_id>', methods=['GET'])
@jwt_required()
def list_seguimientos(consulta_id):
    """Listar seguimientos de una consulta"""
    try:
        seguimientos = SeguimientoPaciente.query.filter_by(consulta_id=consulta_id)\
            .order_by(SeguimientoPaciente.fecha_seguimiento.desc()).all()
        
        return success_response(
            'Seguimientos obtenidos exitosamente',
            [s.to_dict() for s in seguimientos]
        )
        
    except Exception as e:
        return error_response('Error al obtener seguimientos', str(e), 500)

@bp.route('/veterinarios', methods=['GET'])
@jwt_required()
def list_veterinarios():
    """Listar veterinarios activos"""
    try:
        veterinarios = Veterinario.query.filter_by(activo=True).all()
        
        return success_response(
            'Veterinarios obtenidos exitosamente',
            [v.to_dict() for v in veterinarios]
        )
        
    except Exception as e:
        return error_response('Error al obtener veterinarios', str(e), 500)

@bp.route('/veterinarios', methods=['POST'])
@role_required('Administrador')
def create_veterinario(current_user):
    """Crear nuevo veterinario (solo admin)"""
    try:
        data = request.get_json()
        
        veterinario = Veterinario(**data)
        veterinario.save()
        
        return success_response(
            'Veterinario creado exitosamente',
            veterinario.to_dict(),
            201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear veterinario', str(e), 500)

