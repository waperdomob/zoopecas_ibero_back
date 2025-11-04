from app.extensions import db
from app.models.base import BaseModel
from sqlalchemy import Index, CheckConstraint
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Mascota(BaseModel):
    __tablename__ = 'mascotas'
    
    mascota_id = db.Column('mascota_id', db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.cliente_id', ondelete='CASCADE'), 
                          nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(10), nullable=False)
    peso_actual = db.Column(db.Numeric(6, 2))
    color = db.Column(db.String(100))
    microchip = db.Column(db.String(50))
    esterilizado = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.Date, default=db.func.current_date())
    activo = db.Column(db.Boolean, default=True, nullable=False)
    observaciones = db.Column(db.Text)
    
    # Relaciones
    propietario = db.relationship('Cliente', back_populates='mascotas')
    citas = db.relationship('Cita', back_populates='mascota', lazy='dynamic', 
                            cascade='all, delete-orphan')
    historia_clinica = db.relationship('HistoriaClinica', back_populates='mascota', uselist=False, 
                                        cascade='all, delete-orphan')
    vacunaciones = db.relationship('Vacunacion', back_populates='mascota', lazy='dynamic', 
                                  cascade='all, delete-orphan')

    
    # Constraints
    __table_args__ = (
        CheckConstraint("sexo IN ('Macho', 'Hembra')", name='check_sexo'),
        Index('idx_mascotas_cliente', 'cliente_id'),
        Index('idx_mascotas_nombre', 'nombre'),
        Index('idx_mascotas_microchip', 'microchip'),
    )
    
    @property
    def id(self):
        """Alias para compatibilidad"""
        return self.mascota_id
    
    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        
        today = datetime.now().date()
        edad = relativedelta(today, self.fecha_nacimiento)
        
        if edad.years > 0:
            return f"{edad.years} año{'s' if edad.years > 1 else ''}"
        elif edad.months > 0:
            return f"{edad.months} mes{'es' if edad.months > 1 else ''}"
        else:
            return f"{edad.days} día{'s' if edad.days > 1 else ''}"
    
    @property
    def edad_meses(self):
        if not self.fecha_nacimiento:
            return None
        today = datetime.now().date()
        edad = relativedelta(today, self.fecha_nacimiento)
        return edad.years * 12 + edad.months
    
    def to_dict(self, include_relations=True):
        data = {
            'id': self.mascota_id,
            'mascota_id': self.mascota_id,
            'cliente_id': self.cliente_id,
            'nombre': self.nombre,
            'especie': self.especie,
            'raza': self.raza,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'edad': self.edad,
            'edad_meses': self.edad_meses,
            'sexo': self.sexo,
            'peso_actual': float(self.peso_actual) if self.peso_actual else None,
            'color': self.color,
            'microchip': self.microchip,
            'esterilizado': self.esterilizado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'activo': self.activo,
            'observaciones': self.observaciones
        }
        
        if include_relations:
            data['propietario'] = self.propietario.to_dict()
            if self.historia_clinica:
                data['historia_clinica_id'] = self.historia_clinica.historia_id
        
        return data
    
    @classmethod
    def find_by_microchip(cls, microchip):
        return cls.query.filter_by(microchip=microchip).first()
    
    @classmethod
    def search(cls, query_string):
        search_term = f"%{query_string}%"
        return cls.query.filter(
            db.or_(
                cls.nombre.ilike(search_term),
                cls.microchip.ilike(search_term)
            )
        )
    
    def __repr__(self):
        return f'<Mascota {self.nombre}>'