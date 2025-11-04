from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime, time

class CitaSchema(Schema):
    cita_id = fields.Int(dump_only=True)
    cliente_id = fields.Int(required=True)
    mascota_id = fields.Int(required=True)
    veterinario_id = fields.Int(allow_none=True)
    fecha_cita = fields.Date(required=True)
    hora_cita = fields.Time(required=True)
    motivo = fields.Str(required=True, validate=validate.Length(min=5, max=255))
    estado = fields.Str(missing='Programada', validate=validate.OneOf([
        'Programada', 'Confirmada', 'En curso', 'Completada', 'Cancelada', 'No asistió'
    ]))
    observaciones = fields.Str(allow_none=True)
    activa = fields.Bool(missing=True)
    
    @validates('fecha_cita')
    def validate_fecha_cita(self, value):
        if value < datetime.now().date():
            raise ValidationError('La fecha de la cita no puede ser en el pasado')

class CitaUpdateSchema(Schema):
    veterinario_id = fields.Int(allow_none=True)
    fecha_cita = fields.Date()
    hora_cita = fields.Time()
    motivo = fields.Str(validate=validate.Length(min=5, max=255))
    estado = fields.Str(validate=validate.OneOf([
        'Programada', 'Confirmada', 'En curso', 'Completada', 'Cancelada', 'No asistió'
    ]))
    observaciones = fields.Str(allow_none=True)
    activa = fields.Bool()