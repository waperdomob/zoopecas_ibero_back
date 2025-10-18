# -*- coding: utf-8 -*-
from app.extensions import db
from datetime import datetime

class TimestampMixin:
    """Mixin para agregar timestamps a los modelos"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BaseModel(db.Model):
    """Modelo base con métodos comunes"""
    __abstract__ = True
    
    def save(self):
        """Guardar el objeto en la base de datos"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Eliminar el objeto de la base de datos"""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Actualizar el objeto con los datos proporcionados"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self