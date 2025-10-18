from sqlalchemy import CheckConstraint, Index
from app.extensions import db

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
    usuario = db.relationship(
        'User', 
        backref='movimientos_inventario',
        lazy=True,
    )
    
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