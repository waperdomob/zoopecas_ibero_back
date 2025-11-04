from app.extensions import db
from app.models.base import BaseModel
from sqlalchemy import Index, CheckConstraint

class CategoriaProducto(db.Model):
    __tablename__ = 'categorias_productos'
    
    categoria_id = db.Column('categoria_id', db.Integer, primary_key=True)
    nombre_categoria = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    activa = db.Column(db.Boolean, default=True)
    
    productos = db.relationship('Producto', back_populates='categoria', lazy='dynamic', 
                                cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_categorias_nombre', 'nombre_categoria'),
    )
    
    def to_dict(self):
        return {
            'categoria_id': self.categoria_id,
            'nombre_categoria': self.nombre_categoria,
            'descripcion': self.descripcion,
            'activa': self.activa
        }


class Producto(BaseModel):
    __tablename__ = 'productos'
    
    producto_id = db.Column('producto_id', db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_productos.categoria_id'))
    codigo_producto = db.Column(db.String(50), unique=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    laboratorio = db.Column(db.String(100))
    unidad_medida = db.Column(db.String(50))
    precio_compra = db.Column(db.Numeric(10, 2))
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    fecha_vencimiento = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text)
    
    categoria = db.relationship('CategoriaProducto', back_populates='productos')
    detalles = db.relationship('DetalleFactura', back_populates='producto', lazy='dynamic', 
                              cascade='all, delete-orphan')
    movimientos = db.relationship('MovimientoInventario', back_populates='producto', lazy='dynamic')
    
    __table_args__ = (
        Index('idx_productos_codigo', 'codigo_producto'),
        Index('idx_productos_nombre', 'nombre'),
        Index('idx_productos_categoria', 'categoria_id'),
        Index('idx_productos_stock', 'stock_actual'),
    )
    
    @property
    def id(self):
        return self.producto_id
    
    def to_dict(self):
        return {
            'producto_id': self.producto_id,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.nombre_categoria if self.categoria else None,
            'codigo_producto': self.codigo_producto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'laboratorio': self.laboratorio,
            'unidad_medida': self.unidad_medida,
            'precio_compra': float(self.precio_compra) if self.precio_compra else None,
            'precio_venta': float(self.precio_venta),
            'stock_actual': self.stock_actual,
            'stock_minimo': self.stock_minimo,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'activo': self.activo,
            'observaciones': self.observaciones
        }


class MovimientoInventario(db.Model):
    __tablename__ = 'movimientos_inventario'
    
    movimiento_id = db.Column('movimiento_id', db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)
    tipo_movimiento = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2))
    fecha_movimiento = db.Column(db.DateTime, default=db.func.current_timestamp())
    motivo = db.Column(db.String(255))
    documento_referencia = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    
    # Definir la relación con back_populates
    usuario = db.relationship('User', back_populates='movimientos')
    producto = db.relationship('Producto', back_populates='movimientos')
    
    __table_args__ = (
        CheckConstraint("tipo_movimiento IN ('Entrada', 'Salida', 'Ajuste')", 
                        name='check_tipo_movimiento'),
        Index('idx_movimientos_producto', 'producto_id'),
        Index('idx_movimientos_fecha', 'fecha_movimiento'),
        Index('idx_movimientos_tipo', 'tipo_movimiento'),
    )
    
    def to_dict(self):
        return {
            'movimiento_id': self.movimiento_id,
            'producto_id': self.producto_id,
            'producto': self.producto.nombre if self.producto else None,
            'tipo_movimiento': self.tipo_movimiento,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else None,
            'fecha_movimiento': self.fecha_movimiento.isoformat(),
            'motivo': self.motivo,
            'documento_referencia': self.documento_referencia,
            'usuario_id': self.usuario_id,
            'usuario': self.usuario.username if self.usuario else None
        }
