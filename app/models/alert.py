from app.extensions import db
from sqlalchemy import Index, CheckConstraint

class AlertaSistema(db.Model):
    __tablename__ = 'alertas_sistema'
    
    alerta_id = db.Column('alerta_id', db.Integer, primary_key=True)
    tipo_alerta = db.Column(db.String(30), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    leida = db.Column(db.Boolean, default=False)
    usuario_destinatario = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'))
    
    __table_args__ = (
        CheckConstraint("tipo_alerta IN ('Stock Bajo', 'Vencimiento Producto', 'Vencimiento Vacuna', 'Cita Próxima', 'Pago Pendiente', 'Sistema')", 
                       name='check_tipo_alerta'),
        Index('idx_alertas_usuario', 'usuario_destinatario'),
        Index('idx_alertas_leida', 'leida'),
        Index('idx_alertas_tipo', 'tipo_alerta'),
        Index('idx_alertas_fecha', 'fecha_creacion'),
    )
    
    def to_dict(self):
        return {
            'alerta_id': self.alerta_id,
            'tipo_alerta': self.tipo_alerta,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'leida': self.leida,
            'usuario_destinatario': self.usuario_destinatario
        }

