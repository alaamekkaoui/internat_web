# utils/decorators.py
from functools import wraps
from flask import session, request, flash, redirect, url_for, current_app
import secrets

def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # if 'user_id' not in session:
            #     # flash('Please log in to access this page.', 'warning')
            #     # return redirect(url_for('auth.login')) # Assuming 'auth.login' is your login route

            user_role = session.get('role')
            if user_role not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                # Redirect to a general page or a specific 'unauthorized' page
                # For now, redirecting to the home page specified by url_for('index')
                # 'index' is the name of the main route in app.py
                return redirect(url_for('index')) 
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page', 'warning')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('home.home'))
        return f(*args, **kwargs)
    return decorated_function

def csrf_protect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = session.get('csrf_token')
            if not token or token != request.form.get('csrf_token'):
                flash('Erreur de sécurité. Veuillez réessayer.', 'danger')
                return redirect(request.url)
        return f(*args, **kwargs)
    return decorated_function

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']
