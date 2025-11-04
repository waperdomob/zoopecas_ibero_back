from app.extensions import db
from app.models.base import BaseModel
from sqlalchemy import Index, CheckConstraint

class Factura(BaseModel):
    __tablename__ = 'facturas'
    
    factura_id = db.Column('factura_id', db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.cliente_id'), nullable=False)
    numero_factura = db.Column(db.String(50), nullable=False, unique=True)
    fecha_factura = db.Column(db.Date, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    impuestos = db.Column(db.Numeric(10, 2), default=0.00)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='Pendiente')
    observaciones = db.Column(db.Text)
    
    cliente = db.relationship('Cliente', back_populates='facturas')
    detalles = db.relationship('DetalleFactura', back_populates='factura', lazy='dynamic', 
                              cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint("metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia', 'Otro')", 
                       name='check_metodo_pago'),
        CheckConstraint("estado IN ('Pagada', 'Pendiente', 'Anulada')", 
                       name='check_estado_factura'),
        Index('idx_facturas_numero', 'numero_factura'),
        Index('idx_facturas_fecha', 'fecha_factura'),
        Index('idx_facturas_cliente', 'cliente_id'),
        Index('idx_facturas_estado', 'estado'),
    )
    
    @property
    def id(self):
        return self.factura_id
    
    def to_dict(self, include_detalles=False):
        data = {
            'factura_id': self.factura_id,
            'cliente_id': self.cliente_id,
            'numero_factura': self.numero_factura,
            'fecha_factura': self.fecha_factura.isoformat(),
            'subtotal': float(self.subtotal),
            'impuestos': float(self.impuestos),
            'total': float(self.total),
            'metodo_pago': self.metodo_pago,
            'estado': self.estado,
            'observaciones': self.observaciones
        }
        
        if include_detalles:
            data['cliente'] = self.cliente.to_dict() if self.cliente else None
            data['detalles'] = [d.to_dict() for d in self.detalles.all()]
        
        return data


class DetalleFactura(db.Model):
    __tablename__ = 'detalles_factura'
    
    detalle_id = db.Column('detalle_id', db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.factura_id', ondelete='CASCADE'), 
                          nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'))
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.consulta_id'))
    vacunacion_id = db.Column(db.Integer, db.ForeignKey('vacunaciones.vacunacion_id'))
    tipo_item = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    factura = db.relationship('Factura', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalles')
    consulta = db.relationship('Consulta', back_populates='detalles')
    vacunacion = db.relationship('Vacunacion', back_populates='detalles')
    
    __table_args__ = (
        CheckConstraint("tipo_item IN ('Producto', 'Consulta', 'Vacuna', 'Servicio')", 
                       name='check_tipo_item'),
        Index('idx_detalles_factura', 'factura_id'),
    )
    
    def to_dict(self):
        return {
            'detalle_id': self.detalle_id,
            'factura_id': self.factura_id,
            'producto_id': self.producto_id,
            'consulta_id': self.consulta_id,
            'vacunacion_id': self.vacunacion_id,
            'tipo_item': self.tipo_item,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.subtotal)
        }
