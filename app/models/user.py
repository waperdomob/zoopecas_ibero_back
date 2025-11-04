# -*- coding: utf-8 -*-
from app.extensions import db, bcrypt
from app.models.base import BaseModel, TimestampMixin
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import Index, CheckConstraint
from enum import Enum
import traceback

class UserRole(Enum):
    ADMINISTRADOR = "Administrador"
    VETERINARIO = "Veterinario"      
    ASISTENTE = "Asistente"        
    RECEPCIONISTA = "Recepcionista"

class User(BaseModel):
    __tablename__ = 'usuarios'
    
    usuario_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Información personal
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    
    # Configuraciones
    rol = db.Column(db.String(20), nullable=False, default=UserRole.ASISTENTE.value)
    fecha_creacion = db.Column(db.Date, default=db.func.current_date())
    activo = db.Column(db.Boolean, default=True, nullable=False)
    ultimo_acceso = db.Column(db.DateTime)
    
    movimientos = db.relationship('MovimientoInventario', back_populates='usuario', lazy='dynamic')

    __table_args__ = (
        CheckConstraint("rol IN ('Administrador', 'Veterinario', 'Asistente', 'Recepcionista')", 
                       name='check_rol'),
        Index('idx_usuarios_username', 'username'),
        Index('idx_usuarios_rol', 'rol'),
    )
    
    @property
    def id(self):
        """Alias para compatibilidad con JWT"""
        return self.usuario_id
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
    
    def set_password(self, password):
        """Encriptar y establecer la contraseña"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verificar la contraseña"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_tokens(self):
        """Generar tokens JWT"""
        try:
            additional_claims = {
                "rol": self.rol,
                "nombre_completo": f"{self.nombre} {self.apellidos}"
            }
            
            access_token = create_access_token(
                identity=str(self.id),
                additional_claims=additional_claims
            )
            refresh_token = create_refresh_token(identity=str(self.id))
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': self.id,
                    'username': self.username,
                    'email': self.email,
                    'nombre': self.nombre,
                    'apellidos': self.apellidos,
                    'rol': self.rol
                }
            }
        except Exception as e:
            traceback.print_exc()
            raise e
    
    def has_permission(self, required_roles):
        """Verificar si el usuario tiene los permisos necesarios"""
        if isinstance(required_roles, str):
            required_roles = [required_roles]
        return self.rol in required_roles
    
    @classmethod
    def find_by_username(cls, username):
        try:
            return cls.query.filter_by(username=username).first()
        except Exception as e:
            print(f"Error finding user by username: {e}")
            return None
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    def __repr__(self):
        return f'<User {self.username}>'