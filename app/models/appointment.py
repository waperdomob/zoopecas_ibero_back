from app.extensions import db
from app.models.base import BaseModel
from sqlalchemy import Index, CheckConstraint

class Cita(BaseModel):
    __tablename__ = 'citas'
    
    cita_id = db.Column('cita_id', db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.cliente_id'), nullable=False)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.mascota_id'), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('veterinarios.veterinario_id'))
    fecha_cita = db.Column(db.Date, nullable=False)
    hora_cita = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), default='Programada')
    observaciones = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    activa = db.Column(db.Boolean, default=True)
    
    cliente = db.relationship('Cliente', back_populates='citas')
    mascota = db.relationship('Mascota', back_populates='citas')
    veterinario = db.relationship('Veterinario', back_populates='citas')

    __table_args__ = (
        CheckConstraint("estado IN ('Programada', 'Confirmada', 'En curso', 'Completada', 'Cancelada', 'No asistió')", 
                       name='check_estado_cita'),
        Index('idx_citas_fecha', 'fecha_cita', 'hora_cita'),
        Index('idx_citas_cliente', 'cliente_id'),
        Index('idx_citas_mascota', 'mascota_id'),
        Index('idx_citas_veterinario', 'veterinario_id'),
        Index('idx_citas_estado', 'estado'),
    )
    
    @property
    def id(self):
        return self.cita_id
    
    def to_dict(self, include_relations=False):
        data = {
            'cita_id': self.cita_id,
            'cliente_id': self.cliente_id,
            'mascota_id': self.mascota_id,
            'veterinario_id': self.veterinario_id,
            'fecha_cita': self.fecha_cita.isoformat(),
            'hora_cita': self.hora_cita.isoformat(),
            'motivo': self.motivo,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'activa': self.activa
        }
        
        if include_relations:
            data['cliente'] = self.cliente.to_dict() if self.cliente else None
            data['mascota'] = self.mascota.to_dict() if self.mascota else None
            data['veterinario'] = self.veterinario.to_dict() if self.veterinario else None
        
        return data