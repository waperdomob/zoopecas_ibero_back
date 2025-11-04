from marshmallow import Schema, fields, validates, ValidationError, validate
from app.models.pet import Mascota
from datetime import datetime

class MascotaSchema(Schema):
    mascota_id = fields.Int(dump_only=True)
    cliente_id = fields.Int(required=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    especie = fields.Str(required=True, validate=validate.Length(max=50))
    raza = fields.Str(allow_none=True, validate=validate.Length(max=100))
    fecha_nacimiento = fields.Date(allow_none=True)
    sexo = fields.Str(required=True, validate=validate.OneOf(['Macho', 'Hembra']))
    peso_actual = fields.Decimal(places=2, allow_none=True)
    color = fields.Str(allow_none=True, validate=validate.Length(max=100))
    microchip = fields.Str(allow_none=True, validate=validate.Length(max=50))
    esterilizado = fields.Bool(missing=False)
    fecha_registro = fields.Date(dump_only=True)
    activo = fields.Bool(missing=True)
    observaciones = fields.Str(allow_none=True)
    
    @validates('microchip')
    def validate_microchip_unique(self, value):
        if value:
            mascota = Mascota.find_by_microchip(value)
            if mascota and (not hasattr(self, 'instance') or mascota.mascota_id != self.instance.mascota_id):
                raise ValidationError('El microchip ya está registrado')
    
    @validates('fecha_nacimiento')
    def validate_fecha_nacimiento(self, value):
        if value and value > datetime.now().date():
            raise ValidationError('La fecha de nacimiento no puede ser futura')

class MascotaUpdateSchema(Schema):
    nombre = fields.Str(validate=validate.Length(min=2, max=100))
    especie = fields.Str(validate=validate.Length(max=50))
    raza = fields.Str(allow_none=True, validate=validate.Length(max=100))
    fecha_nacimiento = fields.Date(allow_none=True)
    sexo = fields.Str(validate=validate.OneOf(['Macho', 'Hembra']))
    peso_actual = fields.Decimal(places=2, allow_none=True)
    color = fields.Str(allow_none=True)
    microchip = fields.Str(allow_none=True)
    esterilizado = fields.Bool()
    activo = fields.Bool()
    observaciones = fields.Str(allow_none=True)