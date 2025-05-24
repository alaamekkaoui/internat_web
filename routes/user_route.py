from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User
from werkzeug.security import check_password_hash, generate_password_hash
from controllers.user_controller import UserController
from utils.auth import login_required, admin_required

user_bp = Blueprint('user', __name__)
user_controller = UserController()

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Veuillez remplir tous les champs', 'danger')
            return render_template('user/login.html')
        
        user = User().get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session.clear()  # Clear any existing session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session.permanent = True  # Make session persistent
            
            flash('Connexion réussie!', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('user/login.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'user')  # Default to 'user' if not specified
        
        # Basic validation
        if not all([username, password, confirm_password]):
            flash('Veuillez remplir tous les champs', 'danger')
            return render_template('user/register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return render_template('user/register.html')
        
        # Check if username already exists
        existing_user = User().get_user_by_username(username)
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris', 'danger')
            return render_template('user/register.html')
        
        # Create new user
        try:
            success, message = user_controller.create_user(username, password, role)
            if success:
                flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('user.login'))
            else:
                flash(message, 'danger')
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            flash('Une erreur est survenue lors de l\'inscription', 'danger')
    
    return render_template('user/register.html')

@user_bp.route('/logout')
@login_required
def logout():
    username = session.get('username')
    session.clear()
    flash(f'Au revoir {username}! Vous avez été déconnecté', 'info')
    return redirect(url_for('user.login'))

@user_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = user_controller.list_users()
    return render_template('user/list.html', users=users)

@user_bp.route('/profile')
@login_required
def profile():
    user = user_controller.get_user_by_id(session.get('user_id'))
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('home.home'))
    return render_template('user/profile.html', user=user)

@user_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return redirect(url_for('user.change_password'))
        
        success, message = user_controller.change_password(
            session.get('user_id'),
            current_password,
            new_password
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('user.profile'))
        flash(message, 'danger')
    
    return render_template('user/change_password.html')

@user_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    success, message = user_controller.delete_user(user_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('user.list_users'))
