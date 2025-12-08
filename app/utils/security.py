"""
Funções de segurança e validação
Extraídas do sne_radar_web.py para organização modular
"""
import re
import bcrypt


def sanitize_input(text):
    """Sanitiza entrada de texto para prevenir XSS e injeção"""
    if not text:
        return ""
    
    # Remover caracteres perigosos
    text = re.sub(r'[<>"\']', '', str(text))
    text = text.strip()
    
    # Limitar tamanho
    if len(text) > 100:
        text = text[:100]
    
    return text


def validate_username(username):
    """Valida formato do username"""
    if not username:
        return False, "Username é obrigatório"
    
    username = sanitize_input(username)
    
    # Verificar formato (apenas letras, números e underscore)
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return False, "Username deve ter 3-20 caracteres (apenas letras, números e _)"
    
    return True, username


def validate_password(password):
    """Valida força da senha"""
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 3:
        return False, "Senha deve ter pelo menos 3 caracteres"
    
    return True, password


def hash_password(password):
    """Cria hash seguro da senha"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def verify_password(password, hashed):
    """Verifica senha contra hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

