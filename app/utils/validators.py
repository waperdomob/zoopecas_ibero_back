import re
from typing import List, Dict, Any

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validar campos requeridos"""
    errors = []
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"El campo {field} es requerido")
    return errors

def validate_email_format(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_format(phone: str) -> bool:
    """Validar formato de teléfono"""
    pattern = r'^\+?[\d\s\-\(\)]{10,}$'
    return bool(re.match(pattern, phone))