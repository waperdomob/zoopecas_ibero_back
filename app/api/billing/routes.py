from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api.billing import bp
from app.models.billing import Factura, DetalleFactura
from app.models.client import Cliente
from app.models.inventory import Producto, MovimientoInventario
from app.schemas.billing_schemas import FacturaSchema, FacturaUpdateSchema
from app.extensions import db
from app.utils.pagination import paginate_query
from app.utils.responses import success_response, error_response
from app.auth.decorators import role_required, get_current_user
from marshmallow import ValidationError
from datetime import datetime
from decimal import Decimal

factura_schema = FacturaSchema()
facturas_schema = FacturaSchema(many=True)
factura_update_schema = FacturaUpdateSchema()

def generar_numero_factura():
    """Generar número de factura consecutivo"""
    ultima_factura = Factura.query.order_by(Factura.factura_id.desc()).first()
    
    if ultima_factura:
        # Extraer número de la última factura
        try:
            ultimo_numero = int(ultima_factura.numero_factura.split('-')[1])
            nuevo_numero = ultimo_numero + 1
        except:
            nuevo_numero = 1
    else:
        nuevo_numero = 1
    
    return f"FAC-{nuevo_numero:06d}"

@bp.route('', methods=['POST'])
@role_required('Administrador', 'Recepcionista')
def create_factura(current_user):
    """Crear nueva factura"""
    try:
        data = request.get_json()
        
        # Validar cliente
        cliente = Cliente.query.get(data.get('cliente_id'))
        if not cliente:
            return error_response('Cliente no encontrado', None, 404)
        
        # Validar detalles
        if not data.get('detalles') or len(data['detalles']) == 0:
            return error_response('La factura debe tener al menos un detalle', None, 400)
        
        # Calcular totales
        subtotal = Decimal('0.00')
        detalles_validados = []
        
        for detalle in data['detalles']:
            cantidad = detalle['cantidad']
            precio_unitario = Decimal(str(detalle['precio_unitario']))
            subtotal_item = cantidad * precio_unitario
            
            detalle['subtotal'] = subtotal_item
            subtotal += subtotal_item
            
            # Validar stock si es producto
            if detalle.get('tipo_item') == 'Producto' and detalle.get('producto_id'):
                producto = Producto.query.get(detalle['producto_id'])
                if not producto:
                    return error_response(f"Producto ID {detalle['producto_id']} no encontrado", None, 404)
                
                if producto.stock_actual < cantidad:
                    return error_response(
                        f"Stock insuficiente para {producto.nombre}. Stock actual: {producto.stock_actual}",
                        None, 400
                    )
            
            detalles_validados.append(detalle)
        
        # Calcular impuestos (19% IVA)
        impuestos = subtotal * Decimal('0.19')
        total = subtotal + impuestos
        
        # Crear factura
        factura = Factura(
            cliente_id=data['cliente_id'],
            numero_factura=generar_numero_factura(),
            fecha_factura=data['fecha_factura'],
            subtotal=subtotal,
            impuestos=impuestos,
            total=total,
            metodo_pago=data['metodo_pago'],
            estado=data.get('estado', 'Pendiente'),
            observaciones=data.get('observaciones')
        )
        factura.save()
        
        # Crear detalles
        for detalle_data in detalles_validados:
            detalle = DetalleFactura(
                factura_id=factura.factura_id,
                producto_id=detalle_data.get('producto_id'),
                consulta_id=detalle_data.get('consulta_id'),
                vacunacion_id=detalle_data.get('vacunacion_id'),
                tipo_item=detalle_data['tipo_item'],
                descripcion=detalle_data['descripcion'],
                cantidad=detalle_data['cantidad'],
                precio_unitario=detalle_data['precio_unitario'],
                subtotal=detalle_data['subtotal']
            )
            detalle.save()
            
            # Registrar movimiento de inventario si es producto
            if detalle_data['tipo_item'] == 'Producto' and detalle_data.get('producto_id'):
                movimiento = MovimientoInventario(
                    producto_id=detalle_data['producto_id'],
                    tipo_movimiento='Salida',
                    cantidad=detalle_data['cantidad'],
                    precio_unitario=detalle_data['precio_unitario'],
                    motivo='Venta',
                    documento_referencia=factura.numero_factura,
                    usuario_id=current_user.usuario_id
                )
                movimiento.save()
        
        return success_response(
            'Factura creada exitosamente',
            factura.to_dict(include_detalles=True),
            201
        )
        
    except ValidationError as e:
        db.session.rollback()
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear factura', str(e), 500)

@bp.route('', methods=['GET'])
@jwt_required()
def list_facturas():
    """Listar facturas con filtros"""
    try:
        # Filtros
        cliente_id = request.args.get('cliente_id', type=int)
        estado = request.args.get('estado')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        numero_factura = request.args.get('numero_factura')
        
        query = Factura.query
        
        if cliente_id:
            query = query.filter_by(cliente_id=cliente_id)
        
        if estado:
            query = query.filter_by(estado=estado)
        
        if fecha_desde:
            query = query.filter(Factura.fecha_factura >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Factura.fecha_factura <= fecha_hasta)
        
        if numero_factura:
            query = query.filter(Factura.numero_factura.ilike(f"%{numero_factura}%"))
        
        query = query.order_by(Factura.fecha_factura.desc())
        
        pagination = paginate_query(query)
        
        return success_response(
            'Facturas obtenidas exitosamente',
            {
                'facturas': [f.to_dict(include_detalles=False) for f in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        return error_response('Error al obtener facturas', str(e), 500)

@bp.route('/<int:factura_id>', methods=['GET'])
@jwt_required()
def get_factura(factura_id):
    """Obtener factura por ID"""
    try:
        factura = Factura.query.get_or_404(factura_id)
        
        return success_response(
            'Factura obtenida exitosamente',
            factura.to_dict(include_detalles=True)
        )
        
    except Exception as e:
        return error_response('Factura no encontrada', str(e), 404)

@bp.route('/numero/<numero_factura>', methods=['GET'])
@jwt_required()
def get_factura_by_numero(numero_factura):
    """Obtener factura por número"""
    try:
        factura = Factura.query.filter_by(numero_factura=numero_factura).first_or_404()
        
        return success_response(
            'Factura obtenida exitosamente',
            factura.to_dict(include_detalles=True)
        )
        
    except Exception as e:
        return error_response('Factura no encontrada', str(e), 404)

@bp.route('/<int:factura_id>', methods=['PUT'])
@role_required('Administrador', 'Recepcionista')
def update_factura(factura_id, current_user):
    """Actualizar factura"""
    try:
        factura = Factura.query.get_or_404(factura_id)
        data = request.get_json()
        
        # No permitir cambios si está anulada
        if factura.estado == 'Anulada':
            return error_response('No se puede modificar una factura anulada', None, 400)
        
        validated_data = factura_update_schema.load(data)
        factura.update(**validated_data)
        
        return success_response(
            'Factura actualizada exitosamente',
            factura.to_dict(include_detalles=True)
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al actualizar factura', str(e), 500)

@bp.route('/<int:factura_id>/anular', methods=['POST'])
@role_required('Administrador')
def anular_factura(factura_id, current_user):
    """Anular factura"""
    try:
        factura = Factura.query.get_or_404(factura_id)
        
        if factura.estado == 'Anulada':
            return error_response('La factura ya está anulada', None, 400)
        
        # Reversar movimientos de inventario
        for detalle in factura.detalles.all():
            if detalle.tipo_item == 'Producto' and detalle.producto_id:
                # Crear movimiento de entrada para reversar
                movimiento = MovimientoInventario(
                    producto_id=detalle.producto_id,
                    tipo_movimiento='Entrada',
                    cantidad=detalle.cantidad,
                    precio_unitario=detalle.precio_unitario,
                    motivo='Anulación de factura',
                    documento_referencia=factura.numero_factura,
                    usuario_id=current_user.usuario_id
                )
                movimiento.save()
        
        factura.update(estado='Anulada')
        
        return success_response(
            'Factura anulada exitosamente',
            factura.to_dict(include_detalles=True)
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al anular factura', str(e), 500)

@bp.route('/<int:factura_id>/pagar', methods=['POST'])
@role_required('Administrador', 'Recepcionista')
def pagar_factura(factura_id, current_user):
    """Marcar factura como pagada"""
    try:
        factura = Factura.query.get_or_404(factura_id)
        
        if factura.estado == 'Anulada':
            return error_response('No se puede pagar una factura anulada', None, 400)
        
        if factura.estado == 'Pagada':
            return error_response('La factura ya está pagada', None, 400)
        
        factura.update(estado='Pagada')
        
        return success_response(
            'Factura marcada como pagada',
            factura.to_dict(include_detalles=True)
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al procesar pago', str(e), 500)

@bp.route('/reportes/ventas', methods=['GET'])
@role_required('Administrador')
def reporte_ventas(current_user):
    """Reporte de ventas"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        if not fecha_desde or not fecha_hasta:
            return error_response('Fechas son requeridas', None, 400)
        
        # Obtener facturas del período
        facturas = Factura.query.filter(
            Factura.fecha_factura.between(fecha_desde, fecha_hasta),
            Factura.estado != 'Anulada'
        ).all()
        
        # Calcular totales
        total_ventas = sum(f.total for f in facturas)
        total_facturas = len(facturas)
        facturas_pagadas = sum(1 for f in facturas if f.estado == 'Pagada')
        facturas_pendientes = sum(1 for f in facturas if f.estado == 'Pendiente')
        
        # Ventas por método de pago
        ventas_por_metodo = {}
        for factura in facturas:
            metodo = factura.metodo_pago
            if metodo not in ventas_por_metodo:
                ventas_por_metodo[metodo] = {'cantidad': 0, 'total': Decimal('0.00')}
            ventas_por_metodo[metodo]['cantidad'] += 1
            ventas_por_metodo[metodo]['total'] += factura.total
        
        # Convertir Decimal a float para JSON
        for metodo in ventas_por_metodo:
            ventas_por_metodo[metodo]['total'] = float(ventas_por_metodo[metodo]['total'])
        
        return success_response(
            'Reporte de ventas generado exitosamente',
            {
                'periodo': {
                    'desde': fecha_desde,
                    'hasta': fecha_hasta
                },
                'resumen': {
                    'total_ventas': float(total_ventas),
                    'total_facturas': total_facturas,
                    'facturas_pagadas': facturas_pagadas,
                    'facturas_pendientes': facturas_pendientes,
                    'ticket_promedio': float(total_ventas / total_facturas) if total_facturas > 0 else 0
                },
                'ventas_por_metodo': ventas_por_metodo
            }
        )
        
    except Exception as e:
        return error_response('Error al generar reporte', str(e), 500)

@bp.route('/reportes/productos-vendidos', methods=['GET'])
@role_required('Administrador')
def reporte_productos_vendidos(current_user):
    """Reporte de productos más vendidos"""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        limite = request.args.get('limite', 10, type=int)
        
        if not fecha_desde or not fecha_hasta:
            return error_response('Fechas son requeridas', None, 400)
        
        # Consulta de productos vendidos
        from sqlalchemy import func
        
        productos_vendidos = db.session.query(
            DetalleFactura.producto_id,
            Producto.nombre,
            func.sum(DetalleFactura.cantidad).label('cantidad_total'),
            func.sum(DetalleFactura.subtotal).label('monto_total')
        ).join(
            Factura, DetalleFactura.factura_id == Factura.factura_id
        ).join(
            Producto, DetalleFactura.producto_id == Producto.producto_id
        ).filter(
            DetalleFactura.tipo_item == 'Producto',
            Factura.fecha_factura.between(fecha_desde, fecha_hasta),
            Factura.estado != 'Anulada'
        ).group_by(
            DetalleFactura.producto_id,
            Producto.nombre
        ).order_by(
            func.sum(DetalleFactura.cantidad).desc()
        ).limit(limite).all()
        
        productos_data = [
            {
                'producto_id': p.producto_id,
                'nombre': p.nombre,
                'cantidad_vendida': int(p.cantidad_total),
                'monto_total': float(p.monto_total)
            }
            for p in productos_vendidos
        ]
        
        return success_response(
            'Reporte de productos vendidos generado exitosamente',
            {
                'periodo': {
                    'desde': fecha_desde,
                    'hasta': fecha_hasta
                },
                'productos': productos_data
            }
        )
        
    except Exception as e:
        return error_response('Error al generar reporte', str(e), 500)
