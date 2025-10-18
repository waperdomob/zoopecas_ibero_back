from marshmallow import Schema, fields, validates, ValidationError, post_load
from app.models.user import User, UserRole
from app.auth.utils import validate_email, validate_password

class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    nombre = fields.Str(required=True, validate=lambda x: len(x) >= 2)
    apellidos = fields.Str(required=True, validate=lambda x: len(x) >= 2)
    telefono = fields.Str(allow_none=True)
    rol = fields.Enum(UserRole, by_value=True, missing=UserRole.ASISTENTE)
    
    @validates('username')
    def validate_username(self, value):
        if User.find_by_username(value):
            raise ValidationError('El username ya está en uso')
    
    @validates('email')
    def validate_email_unique(self, value):
        if User.find_by_email(value):
            raise ValidationError('El email ya está en uso')
    
    @validates('password')
    def validate_password_strength(self, value):
        is_valid, message = validate_password(value)
        if not is_valid:
            raise ValidationError(message)

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    nombre = fields.Str(validate=lambda x: len(x) >= 2)
    apellidos = fields.Str(validate=lambda x: len(x) >= 2)
    telefono = fields.Str(allow_none=True)

class UserResponseSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    nombre = fields.Str()
    apellidos = fields.Str()
    telefono = fields.Str()
    rol = fields.Method("get_rol")
    activo = fields.Bool()
    fecha_creacion = fields.DateTime()
    ultimo_acceso = fields.DateTime()
    
    def get_rol(self, obj):
        return obj.rol.value if obj.rol else None