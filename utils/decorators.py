# utils/decorators.py
from functools import wraps
from flask import session, flash, redirect, url_for, current_app

def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login')) # Assuming 'auth.login' is your login route

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
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
