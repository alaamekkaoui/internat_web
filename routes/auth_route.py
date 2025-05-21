from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User

auth_bp = Blueprint('auth', __name__)
user_model = User()

@auth_bp.route('/create-admin', methods=['GET'])
def create_admin():
    """Create default admin user with username 'admin' and password 'admin'"""
    try:
        # Check if admin already exists
        existing_admin = user_model.get_user_by_username('admin')
        if existing_admin:
            flash('L\'administrateur existe déjà!', 'warning')
            return redirect(url_for('auth.login'))
        
        # Create admin user
        hashed_password = generate_password_hash('admin')
        if user_model.create_user(
            username='admin',
            password=hashed_password,
            role='admin'
        ):
            flash('Administrateur créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        else:
            flash('Erreur lors de la création de l\'administrateur', 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        # Validate required fields
        if not username or not password:
            flash('Le nom d\'utilisateur et le mot de passe sont requis', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if username already exists
        existing_user = user_model.get_user_by_username(username)
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris', 'error')
            return redirect(url_for('auth.register'))
        
        # Hash password and create user
        hashed_password = generate_password_hash(password)
        if user_model.create_user(
            username=username,
            password=hashed_password,
            role=role
        ):
            flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Erreur lors de l\'inscription', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Le nom d\'utilisateur et le mot de passe sont requis', 'error')
            return redirect(url_for('auth.login'))
        
        user = user_model.get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Connexion réussie!', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('auth.login'))
