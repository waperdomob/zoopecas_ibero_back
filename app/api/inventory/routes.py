from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api.inventory import bp
from app.models.inventory import Producto, CategoriaProducto, MovimientoInventario
from app.schemas.inventory_schemas import (
    ProductoSchema, ProductoUpdateSchema, 
    CategoriaProductoSchema, MovimientoInventarioSchema
)
from app.extensions import db
from app.utils.pagination import paginate_query
from app.utils.responses import success_response, error_response
from app.auth.decorators import role_required, get_current_user
from marshmallow import ValidationError
from datetime import datetime, timedelta

producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)
producto_update_schema = ProductoUpdateSchema()
categoria_schema = CategoriaProductoSchema()
movimiento_schema = MovimientoInventarioSchema()

# ============ CATEGORÍAS ============

@bp.route('/categorias', methods=['GET'])
@jwt_required()
def list_categorias():
    """Listar categorías de productos"""
    try:
        categorias = CategoriaProducto.query.filter_by(activa=True).all()
        
        return success_response(
            'Categorías obtenidas exitosamente',
            [c.to_dict() for c in categorias]
        )
        
    except Exception as e:
        return error_response('Error al obtener categorías', str(e), 500)

@bp.route('/categorias', methods=['POST'])
@role_required('Administrador')
def create_categoria(current_user):
    """Crear nueva categoría"""
    try:
        data = request.get_json()
        validated_data = categoria_schema.load(data)
        
        categoria = CategoriaProducto(**validated_data)
        categoria.save()
        
        return success_response(
            'Categoría creada exitosamente',
            categoria.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear categoría', str(e), 500)

# ============ PRODUCTOS ============

@bp.route('/productos', methods=['POST'])
@role_required('Administrador', 'Asistente')
def create_producto(current_user):
    """Crear nuevo producto"""
    try:
        data = request.get_json()
        validated_data = producto_schema.load(data)
        
        # Verificar código único si se proporciona
        if validated_data.get('codigo_producto'):
            existe = Producto.query.filter_by(
                codigo_producto=validated_data['codigo_producto']
            ).first()
            if existe:
                return error_response('El código de producto ya existe', None, 400)
        
        producto = Producto(**validated_data)
        producto.save()
        
        return success_response(
            'Producto creado exitosamente',
            producto.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al crear producto', str(e), 500)

@bp.route('/productos', methods=['GET'])
@jwt_required()
def list_productos():
    """Listar productos con filtros"""
    try:
        # Filtros
        search = request.args.get('search', '')
        categoria_id = request.args.get('categoria_id', type=int)
        stock_bajo = request.args.get('stock_bajo', type=lambda x: x.lower() == 'true')
        por_vencer = request.args.get('por_vencer', type=lambda x: x.lower() == 'true')
        activo = request.args.get('activo', type=lambda x: x.lower() == 'true')
        
        query = Producto.query
        
        # Búsqueda
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Producto.nombre.ilike(search_term),
                    Producto.codigo_producto.ilike(search_term),
                    Producto.laboratorio.ilike(search_term)
                )
            )
        
        # Filtros
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        if stock_bajo:
            query = query.filter(Producto.stock_actual <= Producto.stock_minimo)
        
        if por_vencer:
            fecha_limite = datetime.now().date() + timedelta(days=30)
            query = query.filter(
                Producto.fecha_vencimiento.isnot(None),
                Producto.fecha_vencimiento <= fecha_limite,
                Producto.fecha_vencimiento >= datetime.now().date()
            )
        
        if activo is not None:
            query = query.filter_by(activo=activo)
        
        query = query.order_by(Producto.nombre)
        
        pagination = paginate_query(query)
        
        return success_response(
            'Productos obtenidos exitosamente',
            {
                'productos': [p.to_dict() for p in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        return error_response('Error al obtener productos', str(e), 500)

@bp.route('/productos/<int:producto_id>', methods=['GET'])
@jwt_required()
def get_producto(producto_id):
    """Obtener producto por ID"""
    try:
        producto = Producto.query.get_or_404(producto_id)
        
        return success_response(
            'Producto obtenido exitosamente',
            producto.to_dict()
        )
        
    except Exception as e:
        return error_response('Producto no encontrado', str(e), 404)

@bp.route('/productos/<int:producto_id>', methods=['PUT'])
@role_required('Administrador', 'Asistente')
def update_producto(producto_id, current_user):
    """Actualizar producto"""
    try:
        producto = Producto.query.get_or_404(producto_id)
        data = request.get_json()
        
        validated_data = producto_update_schema.load(data)
        producto.update(**validated_data)
        
        return success_response(
            'Producto actualizado exitosamente',
            producto.to_dict()
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al actualizar producto', str(e), 500)

@bp.route('/productos/<int:producto_id>', methods=['DELETE'])
@role_required('Administrador')
def delete_producto(producto_id, current_user):
    """Desactivar producto"""
    try:
        producto = Producto.query.get_or_404(producto_id)
        producto.update(activo=False)
        
        return success_response('Producto desactivado exitosamente')
        
    except Exception as e:
        db.session.rollback()
        return error_response('Error al desactivar producto', str(e), 500)

# ============ MOVIMIENTOS DE INVENTARIO ============

@bp.route('/movimientos', methods=['POST'])
@jwt_required()
def create_movimiento():
    """Registrar movimiento de inventario"""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        if not current_user:
            return error_response('Usuario no autenticado', None, 401)
        
        validated_data = movimiento_schema.load(data)
        validated_data['usuario_id'] = current_user.usuario_id
        
        # Verificar que el producto existe
        producto = Producto.query.get(validated_data['producto_id'])
        if not producto:
            return error_response('Producto no encontrado', None, 404)
        
        # Verificar stock suficiente para salidas
        if validated_data['tipo_movimiento'] == 'Salida':
            if producto.stock_actual < validated_data['cantidad']:
                return error_response(
                    f'Stock insuficiente. Stock actual: {producto.stock_actual}',
                    None, 400
                )
        
        movimiento = MovimientoInventario(**validated_data)
        movimiento.save()
        
        # El trigger actualiza el stock automáticamente
        
        return success_response(
            'Movimiento registrado exitosamente',
            movimiento.to_dict(),
            201
        )
        
    except ValidationError as e:
        return error_response('Errores de validación', e.messages, 400)
    except Exception as e:
        db.session.rollback()
        return error_response('Error al registrar movimiento', str(e), 500)

@bp.route('/movimientos', methods=['GET'])
@jwt_required()
def list_movimientos():
    """Listar movimientos de inventario"""
    try:
        producto_id = request.args.get('producto_id', type=int)
        tipo_movimiento = request.args.get('tipo_movimiento')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        query = MovimientoInventario.query
        
        if producto_id:
            query = query.filter_by(producto_id=producto_id)
        
        if tipo_movimiento:
            query = query.filter_by(tipo_movimiento=tipo_movimiento)
        
        if fecha_desde:
            query = query.filter(MovimientoInventario.fecha_movimiento >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(MovimientoInventario.fecha_movimiento <= fecha_hasta)
        
        query = query.order_by(MovimientoInventario.fecha_movimiento.desc())
        
        pagination = paginate_query(query)
        
        return success_response(
            'Movimientos obtenidos exitosamente',
            {
                'movimientos': [m.to_dict() for m in pagination.items],
                'pagination': pagination.to_dict()
            }
        )
        
    except Exception as e:
        return error_response('Error al obtener movimientos', str(e), 500)

@bp.route('/alertas', methods=['GET'])
@jwt_required()
def get_alertas_inventario():
    """Obtener alertas de inventario (stock bajo y vencimientos)"""
    try:
        # Stock bajo
        productos_stock_bajo = Producto.query.filter(
            Producto.stock_actual <= Producto.stock_minimo,
            Producto.activo == True
        ).all()
        
        # Por vencer (próximos 30 días)
        fecha_limite = datetime.now().date() + timedelta(days=30)
        productos_por_vencer = Producto.query.filter(
            Producto.fecha_vencimiento.isnot(None),
            Producto.fecha_vencimiento <= fecha_limite,
            Producto.fecha_vencimiento >= datetime.now().date(),
            Producto.activo == True
        ).all()
        
        # Vencidos
        productos_vencidos = Producto.query.filter(
            Producto.fecha_vencimiento.isnot(None),
            Producto.fecha_vencimiento < datetime.now().date(),
            Producto.activo == True
        ).all()
        
        return success_response(
            'Alertas de inventario obtenidas exitosamente',
            {
                'stock_bajo': {
                    'total': len(productos_stock_bajo),
                    'productos': [p.to_dict() for p in productos_stock_bajo]
                },
                'por_vencer': {
                    'total': len(productos_por_vencer),
                    'productos': [p.to_dict() for p in productos_por_vencer]
                },
                'vencidos': {
                    'total': len(productos_vencidos),
                    'productos': [p.to_dict() for p in productos_vencidos]
                }
            }
        )
        
    except Exception as e:
        return error_response('Error al obtener alertas', str(e), 500)
