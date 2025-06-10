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
            print(f"Erreur lors de la création de l'utilisateur: {str(e)}")
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
    print('user_route.list_users appelé')
    users = user_controller.list_users()
    return render_template('user/list.html', users=users)

@user_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    print('user_route.profile appelé')
    user = user_controller.get_user_by_id(session.get('user_id'))
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('home.home'))
    return render_template('user/profile.html', user=user)

@user_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    print('user_route.update_password appelé')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_password or not new_password or not confirm_password:
        flash('Tous les champs sont requis', 'danger')
        return redirect(url_for('user.profile'))

    if new_password != confirm_password:
        flash('Les mots de passe ne correspondent pas', 'danger')
        return redirect(url_for('user.profile'))

    result = user_controller.update_password(
        user_id=session.get('user_id'),
        current_password=current_password,
        new_password=new_password
    )

    if isinstance(result, dict) and 'error' in result:
        flash(result['error'], 'danger')
    else:
        flash('Mot de passe mis à jour avec succès', 'success')

    return redirect(url_for('user.profile'))

@user_bp.route('/users/<int:user_id>/modify', methods=['GET', 'POST'])
@login_required
@admin_required
def modify_user(user_id):
    print('user_route.modify_user appelé')
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'role': request.form.get('role', 'user')
        }
        
        # Don't allow changing admin role if it's the last admin
        if data['role'] != 'admin' and user_controller.is_last_admin(user_id):
            flash('Impossible de retirer le rôle admin du dernier administrateur', 'danger')
            return redirect(url_for('user.list_users'))
            
        success, message = user_controller.update_user_profile(user_id, data)
        if success:
            flash('Profil utilisateur mis à jour avec succès', 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('user.list_users'))
        
    user = user_controller.get_user_by_id(user_id)
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('user.list_users'))
    return render_template('user/modify.html', user=user)

@user_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    print('user_route.delete_user appelé')
    # Prevent self-deletion
    if user_id == session.get('user_id'):
        flash('Vous ne pouvez pas supprimer votre propre compte', 'danger')
        return redirect(url_for('user.list_users'))
        
    # Get user to check role
    user = user_controller.get_user_by_id(user_id)
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('user.list_users'))
        
    # Check if it's the last admin
    if user_controller.is_last_admin(user_id):
        flash('Impossible de supprimer le dernier administrateur', 'danger')
        return redirect(url_for('user.list_users'))
        
    success, message = user_controller.delete_user(user_id)
    if success:
        flash('Utilisateur supprimé avec succès', 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('user.list_users'))
