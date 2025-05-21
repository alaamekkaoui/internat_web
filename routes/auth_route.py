from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
# If User class uses generate_password_hash, ensure it's imported if direct hashing is needed here
# from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')  # Default to 'user' if not specified

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.find_by_username(username)
        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))

        user_obj = User()
        new_user = user_obj.create(username, password, role)
        if new_user:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    if 'user_id' in session:  # If already logged in, redirect to home
        return redirect(url_for('index'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('auth.login'))

        user = User.find_by_username(username)
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Or a dashboard page
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

    if 'user_id' in session:  # If already logged in, redirect to home
        return redirect(url_for('index'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
