from flask import jsonify
from app.utils.exceptions import VeterinaryException

def register_error_handlers(app):
    """Registrar manejadores de errores"""
    
    @app.errorhandler(VeterinaryException)
    def handle_veterinary_exception(error):
        response = {'message': error.message}
        if error.payload:
            response.update(error.payload)
        if hasattr(error, 'errors') and error.errors:
            response['errors'] = error.errors
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Endpoint no encontrado'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'message': 'Método no permitido'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Error interno del servidor'}), 500