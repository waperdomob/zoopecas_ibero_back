# app/config.py
import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    # Codificar la URL de la base de datos para manejar caracteres especiales
    db_password = os.environ.get('DB_PASSWORD', 'vetpass123')
    db_user = os.environ.get('DB_USER', 'vetuser')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'zoopecas_db')
    
    # Construir URL con encoding UTF-8
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{db_user}:{quote_plus(db_password)}'
        f'@{db_host}:{db_port}/{db_name}'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'client_encoding': 'utf8',
        'connect_args': {
            'options': '-c client_encoding=utf8'
        }
    }
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
    JWT_ALGORITHM = 'HS256'
    
    # Pagination
    POSTS_PER_PAGE = 20
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Cambiar a False para menos logs

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}