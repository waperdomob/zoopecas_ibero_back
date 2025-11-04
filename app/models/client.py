from app.extensions import db
from app.models.base import BaseModel
from sqlalchemy import Index

class Cliente(BaseModel):
    __tablename__ = 'clientes'
    
    cliente_id = db.Column('cliente_id', db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    ciudad = db.Column(db.String(100))
    documento_identidad = db.Column(db.String(50), unique=True)
    fecha_registro = db.Column(db.Date, default=db.func.current_date())
    activo = db.Column(db.Boolean, default=True, nullable=False)
    observaciones = db.Column(db.Text)
    
    # Relaciones
    mascotas = db.relationship('Mascota', back_populates='propietario', lazy='dynamic', 
                               cascade='all, delete-orphan')
    citas = db.relationship('Cita', back_populates='cliente', lazy='dynamic')
    facturas = db.relationship('Factura', back_populates='cliente', lazy='dynamic')
    
    # Índices
    __table_args__ = (
        Index('idx_clientes_documento', 'documento_identidad'),
        Index('idx_clientes_telefono', 'telefono'),
        Index('idx_clientes_nombre', 'nombre', 'apellidos'),
    )
    
    @property
    def id(self):
        """Alias para compatibilidad con JWT"""
        return self.cliente_id
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellidos or ''}".strip()
    
    @property
    def mascotas_activas(self):
        return self.mascotas.filter_by(activo=True).all()
    
    @property
    def total_mascotas(self):
        return self.mascotas.count()
    
    def to_dict(self, include_mascotas=False):
        data = {
            'id': self.cliente_id,
            'cliente_id': self.cliente_id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'nombre_completo': self.nombre_completo,
            'documento_identidad': self.documento_identidad,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'activo': self.activo,
            'observaciones': self.observaciones,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'total_mascotas': self.total_mascotas
        }
        
        if include_mascotas:
            data['mascotas'] = [m.to_dict() for m in self.mascotas_activas]
        
        return data
    
    @classmethod
    def find_by_documento(cls, documento):
        return cls.query.filter_by(documento_identidad=documento).first()
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def search(cls, query_string):
        search_term = f"%{query_string}%"
        return cls.query.filter(
            db.or_(
                cls.nombre.ilike(search_term),
                cls.apellidos.ilike(search_term),
                cls.documento_identidad.ilike(search_term),
                cls.telefono.ilike(search_term),
                cls.email.ilike(search_term)
            )
        )
    
    def __repr__(self):
        return f'<Cliente {self.nombre_completo}>'