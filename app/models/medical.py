from app.extensions import db
from app.models.base import BaseModel
from sqlalchemy import Index, CheckConstraint
from datetime import datetime

class Veterinario(BaseModel):
    __tablename__ = 'veterinarios'
    
    veterinario_id = db.Column('veterinario_id', db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    numero_tarjeta_profesional = db.Column(db.String(50), unique=True)
    especialidad = db.Column(db.String(100))
    fecha_ingreso = db.Column(db.Date, default=db.func.current_date())
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    citas = db.relationship('Cita', back_populates='veterinario')
    consultas = db.relationship('Consulta', back_populates='veterinario')
    vacunaciones = db.relationship('Vacunacion', back_populates='veterinario', lazy='dynamic', 
                                  cascade='all, delete-orphan')
    __table_args__ = (
        Index('idx_veterinarios_tarjeta', 'numero_tarjeta_profesional'),
        Index('idx_veterinarios_nombre', 'nombre', 'apellidos'),
    )
    
    @property
    def id(self):
        return self.veterinario_id
    
    @property
    def nombre_completo(self):
        return f"Dr. {self.nombre} {self.apellidos}"
    
    def to_dict(self):
        return {
            'id': self.veterinario_id,
            'veterinario_id': self.veterinario_id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.email,
            'numero_tarjeta_profesional': self.numero_tarjeta_profesional,
            'especialidad': self.especialidad,
            'fecha_ingreso': self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f'<Veterinario {self.nombre_completo}>'


class HistoriaClinica(BaseModel):
    __tablename__ = 'historias_clinicas'
    
    historia_id = db.Column('historia_id', db.Integer, primary_key=True)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.mascota_id', ondelete='CASCADE'), 
                          nullable=False, unique=True, index=True)
    fecha_creacion = db.Column(db.Date, default=db.func.current_date())
    peso_inicial = db.Column(db.Numeric(6, 2))
    
    # Reseña
    caracteristicas_especiales = db.Column(db.Text)
    
    # Anamnesis
    queja_principal = db.Column(db.Text)
    tratamientos_previos = db.Column(db.Text)
    enfermedades_anteriores = db.Column(db.Text)
    cirugias_anteriores = db.Column(db.Text)
    tipo_dieta = db.Column(db.String(20))
    detalle_dieta = db.Column(db.String(255))
    medicina_preventiva = db.Column(db.Text)
    
    activa = db.Column(db.Boolean, default=True, nullable=False)
    observaciones_generales = db.Column(db.Text)
    
    mascota = db.relationship('Mascota', back_populates='historia_clinica')
    consultas = db.relationship('Consulta', back_populates='historia', lazy='dynamic')

    __table_args__ = (
        CheckConstraint("tipo_dieta IN ('Concentrado', 'Barf', 'Casera', 'Mixta', 'Otra')", 
                       name='check_tipo_dieta'),
        Index('idx_historias_mascota', 'mascota_id'),
        Index('idx_historias_fecha', 'fecha_creacion'),
    )
    
    @property
    def id(self):
        return self.historia_id
    
    @property
    def total_consultas(self):
        return self.consultas.count()
    
    @property
    def ultima_consulta(self):
        return self.consultas.first()
    
    def consultas_recientes(self, limit=5):
        return self.consultas.limit(limit).all()
    
    def to_dict(self, include_consultas=False):
        data = {
            'id': self.historia_id,
            'historia_id': self.historia_id,
            'mascota_id': self.mascota_id,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'peso_inicial': float(self.peso_inicial) if self.peso_inicial else None,
            'caracteristicas_especiales': self.caracteristicas_especiales,
            'queja_principal': self.queja_principal,
            'tratamientos_previos': self.tratamientos_previos,
            'enfermedades_anteriores': self.enfermedades_anteriores,
            'cirugias_anteriores': self.cirugias_anteriores,
            'tipo_dieta': self.tipo_dieta,
            'detalle_dieta': self.detalle_dieta,
            'medicina_preventiva': self.medicina_preventiva,
            'activa': self.activa,
            'observaciones_generales': self.observaciones_generales,
            'total_consultas': self.total_consultas
        }
        
        if include_consultas:
            data['consultas'] = [c.to_dict() for c in self.consultas_recientes()]
            if self.ultima_consulta:
                data['ultima_consulta'] = self.ultima_consulta.to_dict()
        
        data['mascota'] = self.mascota.to_dict() if self.mascota else None
        return data
    
    def __repr__(self):
        return f'<HistoriaClinica Mascota:{self.mascota_id}>'


class Consulta(BaseModel):
    __tablename__ = 'consultas'
    
    consulta_id = db.Column('consulta_id', db.Integer, primary_key=True)
    historia_id = db.Column(db.Integer, db.ForeignKey('historias_clinicas.historia_id', ondelete='CASCADE'), 
                           nullable=False, index=True)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('veterinarios.veterinario_id'), nullable=False)
    fecha_consulta = db.Column(db.Date, nullable=False)
    hora_consulta = db.Column(db.Time, nullable=False)
    motivo_consulta = db.Column(db.Text, nullable=False)
    
    # Inspección
    inspeccion_general = db.Column(db.Text)
    
    # Palpación, Percusión y Auscultación
    temperatura = db.Column(db.Numeric(4, 2))
    pulso = db.Column(db.Integer)
    respiracion = db.Column(db.Integer)
    tiempo_llenado_capilar = db.Column(db.Numeric(3, 1))
    hidratacion = db.Column(db.String(50))
    peso = db.Column(db.Numeric(6, 2))
    ganglios = db.Column(db.Text)
    
    # Sistemas
    sistema_digestivo = db.Column(db.Text)
    sistema_respiratorio = db.Column(db.Text)
    sistema_cardiovascular = db.Column(db.Text)
    sistema_urinario = db.Column(db.Text)
    sistema_genital = db.Column(db.Text)
    sistema_nervioso = db.Column(db.Text)
    sistema_locomotor = db.Column(db.Text)
    piel_anexos = db.Column(db.Text)
    hallazgos = db.Column(db.Text)
    
    # Exámenes
    examenes_solicitados = db.Column(db.Text)
    examenes_autorizados = db.Column(db.Text)
    
    # Diagnóstico y Tratamiento
    diagnostico = db.Column(db.Text, nullable=False)
    pronostico = db.Column(db.String(20))
    tratamiento_ideal = db.Column(db.Text)
    tratamiento_instaurado = db.Column(db.Text)
    cotizacion_tratamiento = db.Column(db.Numeric(10, 2))
    
    observaciones = db.Column(db.Text)
    proxima_cita = db.Column(db.Date)
    costo_consulta = db.Column(db.Numeric(10, 2), default=0.00)
    
    historia= db.relationship('HistoriaClinica', back_populates='consultas')
    veterinario = db.relationship('Veterinario', back_populates='consultas')
    detalles = db.relationship('DetalleFactura', back_populates='consulta', lazy='dynamic', 
                              cascade='all, delete-orphan')
    seguimientos = db.relationship('SeguimientoPaciente', back_populates='consulta', lazy='dynamic', 
                                    cascade='all, delete-orphan')
    servicios = db.relationship('ServicioConsulta', back_populates='consulta', lazy='dynamic', 
                               cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint("pronostico IN ('Favorable', 'Desfavorable', 'Reservado')", 
                       name='check_pronostico'),
        Index('idx_consultas_historia', 'historia_id'),
        Index('idx_consultas_veterinario', 'veterinario_id'),
        Index('idx_consultas_fecha', 'fecha_consulta'),
    )
    
    @property
    def id(self):
        return self.consulta_id
    
    @property
    def fecha_hora(self):
        return datetime.combine(self.fecha_consulta, self.hora_consulta)
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.consulta_id,
            'consulta_id': self.consulta_id,
            'historia_id': self.historia_id,
            'veterinario_id': self.veterinario_id,
            'fecha_consulta': self.fecha_consulta.isoformat(),
            'hora_consulta': self.hora_consulta.isoformat(),
            'motivo_consulta': self.motivo_consulta,
            'inspeccion_general': self.inspeccion_general,
            'temperatura': float(self.temperatura) if self.temperatura else None,
            'pulso': self.pulso,
            'respiracion': self.respiracion,
            'tiempo_llenado_capilar': float(self.tiempo_llenado_capilar) if self.tiempo_llenado_capilar else None,
            'hidratacion': self.hidratacion,
            'peso': float(self.peso) if self.peso else None,
            'ganglios': self.ganglios,
            'sistema_digestivo': self.sistema_digestivo,
            'sistema_respiratorio': self.sistema_respiratorio,
            'sistema_cardiovascular': self.sistema_cardiovascular,
            'sistema_urinario': self.sistema_urinario,
            'sistema_genital': self.sistema_genital,
            'sistema_nervioso': self.sistema_nervioso,
            'sistema_locomotor': self.sistema_locomotor,
            'piel_anexos': self.piel_anexos,
            'hallazgos': self.hallazgos,
            'examenes_solicitados': self.examenes_solicitados,
            'examenes_autorizados': self.examenes_autorizados,
            'diagnostico': self.diagnostico,
            'pronostico': self.pronostico,
            'tratamiento_ideal': self.tratamiento_ideal,
            'tratamiento_instaurado': self.tratamiento_instaurado,
            'cotizacion_tratamiento': float(self.cotizacion_tratamiento) if self.cotizacion_tratamiento else None,
            'observaciones': self.observaciones,
            'proxima_cita': self.proxima_cita.isoformat() if self.proxima_cita else None,
            'costo_consulta': float(self.costo_consulta) if self.costo_consulta else None
        }
        
        if include_relations:
            data['veterinario'] = self.veterinario.to_dict() if self.veterinario else None
        
        return data
    
    def __repr__(self):
        return f'<Consulta {self.consulta_id} - {self.fecha_consulta}>'


class SeguimientoPaciente(BaseModel):
    __tablename__ = 'seguimiento_paciente'
    
    seguimiento_id = db.Column('seguimiento_id', db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.consulta_id', ondelete='CASCADE'), 
                           nullable=False)
    fecha_seguimiento = db.Column(db.Date, nullable=False)
    hora_seguimiento = db.Column(db.Time)
    observaciones = db.Column(db.Text, nullable=False)
    responsable = db.Column(db.String(200))
    
    consulta = db.relationship('Consulta', back_populates='seguimientos', lazy=True)

    __table_args__ = (
        Index('idx_seguimiento_consulta', 'consulta_id'),
        Index('idx_seguimiento_fecha', 'fecha_seguimiento'),
    )
    
    def to_dict(self):
        return {
            'seguimiento_id': self.seguimiento_id,
            'consulta_id': self.consulta_id,
            'fecha_seguimiento': self.fecha_seguimiento.isoformat(),
            'hora_seguimiento': self.hora_seguimiento.isoformat() if self.hora_seguimiento else None,
            'observaciones': self.observaciones,
            'responsable': self.responsable
        }


class TipoServicio(db.Model):
    __tablename__ = 'tipos_servicios'
    
    servicio_id = db.Column('servicio_id', db.Integer, primary_key=True)
    nombre_servicio = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_base = db.Column(db.Numeric(10, 2))
    duracion_estimada = db.Column(db.Integer)
    activo = db.Column(db.Boolean, default=True)
    
    servicios_en_consultas = db.relationship('ServicioConsulta', back_populates='tipo_servicio', lazy='dynamic', 
                                            cascade='all, delete-orphan')
    __table_args__ = (
        Index('idx_servicios_nombre', 'nombre_servicio'),
    )
    
    def to_dict(self):
        return {
            'servicio_id': self.servicio_id,
            'nombre_servicio': self.nombre_servicio,
            'descripcion': self.descripcion,
            'precio_base': float(self.precio_base) if self.precio_base else None,
            'duracion_estimada': self.duracion_estimada,
            'activo': self.activo
        }


class ServicioConsulta(db.Model):
    __tablename__ = 'servicios_consulta'
    
    servicio_consulta_id = db.Column('servicio_consulta_id', db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.consulta_id', ondelete='CASCADE'), 
                           nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('tipos_servicios.servicio_id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    observaciones = db.Column(db.Text)
    
    tipo_servicio = db.relationship('TipoServicio', back_populates='servicios_en_consultas', lazy=True)
    consulta = db.relationship('Consulta', back_populates='servicios', lazy=True)
    
    __table_args__ = (
        Index('idx_servicios_consulta', 'consulta_id'),
    )
    
    def to_dict(self):
        return {
            'servicio_consulta_id': self.servicio_consulta_id,
            'consulta_id': self.consulta_id,
            'servicio_id': self.servicio_id,
            'servicio': self.tipo_servicio.nombre_servicio if self.tipo_servicio else None,
            'precio': float(self.precio),
            'observaciones': self.observaciones
        }