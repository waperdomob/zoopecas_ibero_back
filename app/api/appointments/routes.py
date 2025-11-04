from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api.appointments import bp
from app.models.appointment import Cita
from app.models.client import Cliente
from app.models.pet import Mascota
from app.models.medical import Veterinario
from app.schemas.appointment_schemas import CitaSchema, CitaUpdateSchema
from app.extensions import db
from app.utils.pagination import paginate_query
from app.utils.responses import success_response, error_response
from app.auth.decorators import role_required, get_current_user
from marshmallow import ValidationError
from datetime import datetime, timedelta

cita_schema = CitaSchema()
citas_schema = CitaSchema(many=True)
cita_update_schema = CitaUpdateSchema()

@bp.route('', methods=['POST'])
@jwt_required()
def create_cita():
    """Crear nueva cita"""
    try:
        data = request.get_json()
        validated_data = cita_schema.load(data)
        
        # Verificar que el cliente existe
        cliente = Cliente.query.get(validated_data['cliente_id'])
        if not cliente:
            return error_response('Cliente no encontrado', None, 404)
        
        # Verificar que la mascota existe y pertenece al cliente
        mascota = Mascota.query.get(validated_data['mascota_id'])
        if not mascota:
            return error_response('Mascota no encontrada', None, 404)
        if mascota.cliente_id != validated_data['cliente_id']:
            return error_response('La mascota no pertenece a este cliente', None, 400)
        
        # Verificar disponibilidad del veterinario si se especifica
        if validated_data.get('veterinario_id'):
            veterinario = Veterinario.query.get(validated_data['veterinario_id'])
            if not veterinario or not veterinario.activo:
                return error_response('Veterinario no disponible', None, 400)
            
            # Verificar conflicto de horarios
            conflicto = Cita.query.filter(
                Cita.veterinario_id == validated_data['veterinario_id'],
                Cita.fecha_cita == validated_data['fecha_cita'],
                Cita.hora_cita == validated_data['hora_cita'],
                Cita.estado.in_(['Programada', 'Confirmada']),
                Cita.activa == True
            ).first()
            
            if conflicto:
                return error_response(
                    'Ya existe una cita programada para este veterinario en ese horario',
                    None, 400
                )
        
        cita = Cita(**validated_data)
        cita.save()
        
        return success_response(
            'Cita creada exitosamente',
            cita.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear cita', str(e), 500)

@bp.route('', methods=['GET'])
@jwt_required()
def list_citas():
    """Listar citas con filtros"""
    try:
        # Filtros
        fecha = request.args.get('fecha')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        cliente_id = request.args.get('cliente_id', type=int)
        mascota_id = request.args.get('mascota_id', type=int)
        veterinario_id = request.args.get('veterinario_id', type=int)
        estado = request.args.get('estado')
        
        query = Cita.query.filter_by(activa=True)
        
        # Aplicar filtros
        if fecha:
            query = query.filter_by(fecha_cita=fecha)
        
        if fecha_desde:
            query = query.filter(Cita.fecha_cita >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Cita.fecha_cita <= fecha_hasta)
        
        if cliente_id:
            query = query.filter_by(cliente_id=cliente_id)
        
        if mascota_id:
            query = query.filter_by(mascota_id=mascota_id)
        
        if veterinario_id:
            query = query.filter_by(veterinario_id=veterinario_id)
        
        if estado:
            query = query.filter_by(estado=estado)
        
        # Ordenar por fecha y hora
        query = query.order_by(Cita.fecha_cita.desc(), Cita.hora_cita.desc())
        
        pagination = paginate_query(query)
        
        return success_response(
            'Citas obtenidas exitosamente',
            {
                'citas': [c.to_dict() for c in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        return error_response('Error al obtener citas', str(e), 500)

@bp.route('/hoy', methods=['GET'])
@jwt_required()
def get_citas_hoy():
    """Obtener citas del día"""
    try:
        hoy = datetime.now().date()
        
        citas = Cita.query.filter(
            Cita.fecha_cita == hoy,
            Cita.activa == True
        ).order_by(Cita.hora_cita).all()
        
        return success_response(
            'Citas de hoy obtenidas exitosamente',
            [c.to_dict() for c in citas]
        )
        
    except Exception as e:
        return error_response('Error al obtener citas', str(e), 500)

@bp.route('/proximas', methods=['GET'])
@jwt_required()
def get_citas_proximas():
    """Obtener próximas citas (próximos 7 días)"""
    try:
        hoy = datetime.now().date()
        fecha_limite = hoy + timedelta(days=7)
        
        citas = Cita.query.filter(
            Cita.fecha_cita.between(hoy, fecha_limite),
            Cita.estado.in_(['Programada', 'Confirmada']),
            Cita.activa == True
        ).order_by(Cita.fecha_cita, Cita.hora_cita).all()
        
        return success_response(
            'Próximas citas obtenidas exitosamente',
            [c.to_dict() for c in citas]
        )
        
    except Exception as e:
        return error_response('Error al obtener citas', str(e), 500)

@bp.route('/<int:cita_id>', methods=['GET'])
@jwt_required()
def get_cita(cita_id):
    """Obtener cita por ID"""
    try:
        cita = Cita.query.get_or_404(cita_id)
        
        return success_response(
            'Cita obtenida exitosamente',
            cita.to_dict()
        )
        
    except Exception as e:
        return error_response('Cita no encontrada', str(e), 404)

@bp.route('/<int:cita_id>', methods=['PUT'])
@jwt_required()
def update_cita(cita_id):
    """Actualizar cita"""
    try:
        cita = Cita.query.get_or_404(cita_id)
        data = request.get_json()
        
        validated_data = cita_update_schema.load(data)
        
        # Verificar conflicto de horarios si se cambia veterinario, fecha u hora
        if any(k in validated_data for k in ['veterinario_id', 'fecha_cita', 'hora_cita']):
            veterinario_id = validated_data.get('veterinario_id', cita.veterinario_id)
            fecha_cita = validated_data.get('fecha_cita', cita.fecha_cita)
            hora_cita = validated_data.get('hora_cita', cita.hora_cita)
            
            if veterinario_id:
                conflicto = Cita.query.filter(
                    Cita.cita_id != cita_id,
                    Cita.veterinario_id == veterinario_id,
                    Cita.fecha_cita == fecha_cita,
                    Cita.hora_cita == hora_cita,
                    Cita.estado.in_(['Programada', 'Confirmada']),
                    Cita.activa == True
                ).first()
                
                if conflicto:
                    return error_response(
                        'Ya existe una cita en ese horario para este veterinario',
                        None, 400
                    )
        
        cita.update(**validated_data)
        
        return success_response(
            'Cita actualizada exitosamente',
            cita.to_dict()
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al actualizar cita', str(e), 500)

@bp.route('/<int:cita_id>/cancelar', methods=['POST'])
@jwt_required()
def cancel_cita(cita_id):
    """Cancelar cita"""
    try:
        cita = Cita.query.get_or_404(cita_id)
        
        if cita.estado in ['Completada', 'Cancelada']:
            return error_response('No se puede cancelar esta cita', None, 400)
        
        cita.update(estado='Cancelada')
        
        return success_response('Cita cancelada exitosamente', cita.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al cancelar cita', str(e), 500)

@bp.route('/<int:cita_id>/confirmar', methods=['POST'])
@jwt_required()
def confirm_cita(cita_id):
    """Confirmar cita"""
    try:
        cita = Cita.query.get_or_404(cita_id)
        
        if cita.estado != 'Programada':
            return error_response('Solo se pueden confirmar citas programadas', None, 400)
        
        cita.update(estado='Confirmada')
        
        return success_response('Cita confirmada exitosamente', cita.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al confirmar cita', str(e), 500)

@bp.route('/<int:cita_id>/completar', methods=['POST'])
@role_required('Administrador', 'Veterinario')
def complete_cita(cita_id, current_user):
    """Marcar cita como completada"""
    try:
        cita = Cita.query.get_or_404(cita_id)
        
        if cita.estado not in ['Programada', 'Confirmada', 'En curso']:
            return error_response('No se puede completar esta cita', None, 400)
        
        cita.update(estado='Completada')
        
        return success_response('Cita completada exitosamente', cita.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al completar cita', str(e), 500)

@bp.route('/disponibilidad', methods=['GET'])
@jwt_required()
def check_disponibilidad():
    """Verificar disponibilidad de horarios"""
    try:
        fecha = request.args.get('fecha')
        veterinario_id = request.args.get('veterinario_id', type=int)
        
        if not fecha:
            return error_response('Fecha es requerida', None, 400)
        
        # Obtener citas ocupadas
        query = Cita.query.filter(
            Cita.fecha_cita == fecha,
            Cita.estado.in_(['Programada', 'Confirmada', 'En curso']),
            Cita.activa == True
        )
        
        if veterinario_id:
            query = query.filter_by(veterinario_id=veterinario_id)
        
        citas_ocupadas = query.all()
        horarios_ocupados = [c.hora_cita.strftime('%H:%M') for c in citas_ocupadas]
        
        # Generar horarios disponibles (8:00 AM - 6:00 PM, cada 30 min)
        from datetime import time
        horarios_disponibles = []
        for hora in range(8, 18):
            for minuto in [0, 30]:
                horario = time(hora, minuto).strftime('%H:%M')
                if horario not in horarios_ocupados:
                    horarios_disponibles.append(horario)
        
        return success_response(
            'Disponibilidad obtenida exitosamente',
            {
                'fecha': fecha,
                'veterinario_id': veterinario_id,
                'horarios_disponibles': horarios_disponibles,
                'horarios_ocupados': horarios_ocupados
            }
        )
        
    except Exception as e:
        return error_response('Error al verificar disponibilidad', str(e), 500)
