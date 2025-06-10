from models import User
from werkzeug.security import generate_password_hash, check_password_hash

class UserController:
    def __init__(self):
        self.user_model = User()

    def create_user(self, username, password, role='user'):
        """Register a new user"""
        try:
            # Check if username already exists
            if self.user_model.get_user_by_username(username):
                return False, "Ce nom d'utilisateur existe déjà."

            # Create new user
            success, message = self.user_model.create_user(username, password, role)
            return success, message
        except Exception as e:
            return False, f"Erreur lors de l'inscription: {str(e)}"

    def login_user(self, username, password):
        """Authenticate a user"""
        try:
            user = self.user_model.get_user_by_username(username)
            if not user:
                return False, None, "Nom d'utilisateur incorrect."

            if not check_password_hash(user['password'], password):
                return False, None, "Mot de passe incorrect."

            return True, user, "Connexion réussie!"
        except Exception as e:
            return False, None, f"Erreur lors de la connexion: {str(e)}"

    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        try:
            user = self.user_model.get_user_by_id(user_id)
            if not user:
                return False, "Utilisateur non trouvé."

            if not check_password_hash(user['password'], current_password):
                return False, "Mot de passe actuel incorrect."

            success, message = self.user_model.change_password(user_id, current_password, new_password)
            return success, message
        except Exception as e:
            return False, f"Erreur lors du changement de mot de passe: {str(e)}"

    def update_user_profile(self, user_id, data):
        """Update user profile information"""
        try:
            user = self.user_model.get_user_by_id(user_id)
            if not user:
                return False, "Utilisateur non trouvé."

            success, message = self.user_model.update_user(user_id, data)
            return success, message
        except Exception as e:
            return False, f"Erreur lors de la mise à jour du profil: {str(e)}"

    def delete_user(self, user_id):
        """Delete a user"""
        try:
            user = self.user_model.get_user_by_id(user_id)
            if not user:
                return False, "Utilisateur non trouvé."

            success, message = self.user_model.delete_user(user_id)
            return success, message
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"

    def get_user_profile(self, user_id):
        """Get user profile information"""
        try:
            user = self.user_model.get_user_by_id(user_id)
            if user:
                return True, user
            return False, "Utilisateur non trouvé."
        except Exception as e:
            return False, f"Erreur lors de la récupération du profil: {str(e)}"

    def get_all_users(self):
        """Get all users"""
        try:
            users = self.user_model.get_all_users()
            return True, users
        except Exception as e:
            return False, f"Erreur lors de la récupération des utilisateurs: {str(e)}"

    def create_admin_if_not_exists(self):
        """Create default admin user if no users exist"""
        try:
            return self.user_model.create_default_admin()
        except Exception as e:
            print(f"Erreur lors de la création de l'admin par défaut: {str(e)}")
            return False

    def get_user_by_id(self, user_id):
        return self.user_model.get_user_by_id(user_id)

    def list_users(self):
        """Get all users"""
        try:
            users = self.user_model.list_users()
            return users
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
            return []

    def is_last_admin(self, user_id):
        """Check if the user is the last admin in the system"""
        try:
            # Get the user to check their role
            user = self.user_model.get_user_by_id(user_id)
            if not user or user['role'] != 'admin':
                return False
                
            # Count total number of admin users
            admin_count = self.user_model.count_users_by_role('admin')
            return admin_count <= 1
        except Exception as e:
            print(f"Erreur lors de la vérification du dernier admin: {str(e)}")
            return False

    def update_password(self, user_id, current_password, new_password):
        print('user_controller.update_password appelé')
        try:
            # Get user from database
            user = self.get_user_by_id(user_id)
            if not user:
                return {'error': 'Utilisateur non trouvé'}

            # Verify current password
            if not check_password_hash(user['password'], current_password):
                return {'error': 'Mot de passe actuel incorrect'}

            # Update password
            hashed_password = generate_password_hash(new_password)
            success, message = self.user_model.change_password(user_id, current_password, new_password)
            if not success:
                return {'error': message}
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du mot de passe: {str(e)}")
            return {'error': 'Erreur lors de la mise à jour du mot de passe'}
