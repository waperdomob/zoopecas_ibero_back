import re
from app.models.user import User

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validar que la contraseña cumpla con los requisitos"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    return True, "Contraseña válida"

def validate_user_data(data, is_update=False):
    """Validar datos del usuario"""
    errors = []
    
    if not is_update or 'email' in data:
        if not data.get('email') or not validate_email(data['email']):
            errors.append("Email inválido")
        elif User.find_by_email(data['email']):
            errors.append("El email ya está en uso")
    
    if not is_update or 'username' in data:
        if not data.get('username') or len(data['username']) < 3:
            errors.append("El username debe tener al menos 3 caracteres")
        elif User.find_by_username(data['username']):
            errors.append("El username ya está en uso")
    
    if not is_update and 'password' in data:
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            errors.append(message)
    
    required_fields = ['nombre', 'apellidos'] if not is_update else []
    for field in required_fields:
        if not data.get(field):
            errors.append(f"El campo {field} es requerido")
    
    return errors