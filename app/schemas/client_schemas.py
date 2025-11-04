from marshmallow import Schema, fields, validates, ValidationError, validate
from app.models.client import Cliente

class ClienteSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellidos = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    documento_identidad = fields.Str(required=True, validate=validate.Length(min=5, max=50))
    telefono = fields.Str(required=True, validate=validate.Length(min=7, max=20))
    email = fields.Email(allow_none=True)
    direccion = fields.Str(allow_none=True, validate=validate.Length(max=255))
    ciudad = fields.Str(allow_none=True, validate=validate.Length(max=100))
    activo = fields.Bool(missing=True)
    observaciones = fields.Str(allow_none=True)
    
    @validates('documento_identidad')
    def validate_documento_unique(self, value):
        cliente = Cliente.find_by_documento(value)
        if cliente and (not hasattr(self, 'instance') or cliente.id != self.instance.id):
            raise ValidationError('El documento de identidad ya está registrado')
    
    @validates('email')
    def validate_email_unique(self, value):
        if value:
            cliente = Cliente.find_by_email(value)
            if cliente and (not hasattr(self, 'instance') or cliente.id != self.instance.id):
                raise ValidationError('El email ya está registrado')

class ClienteUpdateSchema(Schema):
    nombre = fields.Str(validate=validate.Length(min=2, max=100))
    apellidos = fields.Str(validate=validate.Length(min=2, max=100))
    telefono = fields.Str(validate=validate.Length(min=7, max=20))
    email = fields.Email(allow_none=True)
    direccion = fields.Str(allow_none=True, validate=validate.Length(max=255))
    ciudad = fields.Str(allow_none=True, validate=validate.Length(max=100))
    activo = fields.Bool()
    observaciones = fields.Str(allow_none=True)
