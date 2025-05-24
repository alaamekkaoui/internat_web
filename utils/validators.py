import re

def validate_password(password):
    """
    Validate password strength
    Returns None if password is valid, error message if invalid
    """
    if len(password) < 8:
        return "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r"[A-Z]", password):
        return "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r"[a-z]", password):
        return "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r"\d", password):
        return "Le mot de passe doit contenir au moins un chiffre"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Le mot de passe doit contenir au moins un caractère spécial"
    
    return None

def validate_email(email):
    """
    Validate email format
    Returns True if email is valid, False if invalid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username):
    """
    Validate username format
    Returns None if username is valid, error message if invalid
    """
    if len(username) < 3:
        return "Le nom d'utilisateur doit contenir au moins 3 caractères"
    
    if len(username) > 20:
        return "Le nom d'utilisateur ne doit pas dépasser 20 caractères"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return "Le nom d'utilisateur ne doit contenir que des lettres, chiffres, tirets et underscores"
    
    return None 