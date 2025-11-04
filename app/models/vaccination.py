from app.extensions import db
from sqlalchemy import Index

class VacunaCatalogo(db.Model):
    __tablename__ = 'vacunas_catalogo'
    
    vacuna_id = db.Column('vacuna_id', db.Integer, primary_key=True)
    nombre_vacuna = db.Column(db.String(100), nullable=False)
    laboratorio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    meses_vigencia = db.Column(db.Integer)
    precio = db.Column(db.Numeric(10, 2))
    activa = db.Column(db.Boolean, default=True)
    
    vacunaciones = db.relationship('Vacunacion', back_populates='vacuna', lazy='dynamic', 
                                  cascade='all, delete-orphan')
    __table_args__ = (
        Index('idx_vacunas_nombre', 'nombre_vacuna'),
    )
    
    def to_dict(self):
        return {
            'vacuna_id': self.vacuna_id,
            'nombre_vacuna': self.nombre_vacuna,
            'laboratorio': self.laboratorio,
            'descripcion': self.descripcion,
            'meses_vigencia': self.meses_vigencia,
            'precio': float(self.precio) if self.precio else None,
            'activa': self.activa
        }


class Vacunacion(db.Model):
    __tablename__ = 'vacunaciones'
    
    vacunacion_id = db.Column('vacunacion_id', db.Integer, primary_key=True)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.mascota_id', ondelete='CASCADE'), 
                          nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('veterinarios.veterinario_id'), nullable=False)
    vacuna_id = db.Column(db.Integer, db.ForeignKey('vacunas_catalogo.vacuna_id'), nullable=False)
    fecha_aplicacion = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date)
    lote = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    
    mascota = db.relationship('Mascota', back_populates='vacunaciones', lazy=True)
    veterinario = db.relationship('Veterinario', back_populates='vacunaciones', lazy=True)
    vacuna = db.relationship('VacunaCatalogo', back_populates='vacunaciones', lazy=True)
    detalles = db.relationship('DetalleFactura', back_populates='vacunacion', lazy='dynamic', 
                                cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_vacunaciones_mascota', 'mascota_id'),
        Index('idx_vacunaciones_fecha', 'fecha_aplicacion'),
        Index('idx_vacunaciones_vencimiento', 'fecha_vencimiento'),
    )
    
    def to_dict(self, include_relations=False):
        data = {
            'vacunacion_id': self.vacunacion_id,
            'mascota_id': self.mascota_id,
            'veterinario_id': self.veterinario_id,
            'vacuna_id': self.vacuna_id,
            'fecha_aplicacion': self.fecha_aplicacion.isoformat(),
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'lote': self.lote,
            'observaciones': self.observaciones,
            'costo': float(self.costo) if self.costo else None
        }
        
        if include_relations:
            data['vacuna'] = self.vacuna_catalogo.to_dict() if self.vacuna_catalogo else None
            data['veterinario'] = self.veterinario.to_dict() if self.veterinario else None
        
        return data