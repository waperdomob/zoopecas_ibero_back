from flask import Flask
from .config import config
from .extensions import db, migrate, jwt, bcrypt, cors, ma

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['JSON_AS_ASCII'] = False
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    ma.init_app(app)
    
    with app.app_context():
        from app import models

    # JWT callbacks
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired', 'error': 'token_expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Invalid token', 'error': 'invalid_token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'message': 'Token is required', 'error': 'authorization_required'}, 401
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.api.clients import bp as clients_bp
    app.register_blueprint(clients_bp, url_prefix='/api/clients')
    
    from app.api.medical import bp as medical_bp
    app.register_blueprint(medical_bp, url_prefix='/api/medical')

    from app.api.pets import bp as pets_bp
    app.register_blueprint(pets_bp, url_prefix='/api/pets')
    
    from app.api.appointments import bp as appointments_bp
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    
    # Registrar blueprints de inventario
    from app.api.inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    
    # Registrar blueprints de facturación
    from app.api.billing import bp as billing_bp
    app.register_blueprint(billing_bp, url_prefix='/api/billing')
    
    return app