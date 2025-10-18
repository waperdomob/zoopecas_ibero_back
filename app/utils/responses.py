from flask import jsonify

def success_response(message, data=None, status_code=200):
    """Respuesta de éxito estandardizada"""
    response = {'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message, errors=None, status_code=400):
    """Respuesta de error estandardizada"""
    response = {'message': message}
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code