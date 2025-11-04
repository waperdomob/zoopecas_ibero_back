class VeterinaryException(Exception):
    """Excepción base del sistema veterinario"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

class ValidationError(VeterinaryException):
    """Error de validación"""
    def __init__(self, message, errors=None):
        super().__init__(message, 400)
        self.errors = errors

class AuthenticationError(VeterinaryException):
    """Error de autenticación"""
    def __init__(self, message="Credenciales inválidas"):
        super().__init__(message, 401)

class AuthorizationError(VeterinaryException):
    """Error de autorización"""
    def __init__(self, message="Permisos insuficientes"):
        super().__init__(message, 403)

class NotFoundError(VeterinaryException):
    """Recurso no encontrado"""
    def __init__(self, message="Recurso no encontrado"):
        super().__init__(message, 404)