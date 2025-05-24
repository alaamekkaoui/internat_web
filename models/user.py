from database.db import get_connection
from werkzeug.security import check_password_hash, generate_password_hash

class User:
    def __init__(self):
        self.conn = get_connection()
    
    def create_user(self, username, password, role='user'):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                (username, generate_password_hash(password), role)
            )
            self.conn.commit()
            return True, 'Utilisateur créé avec succès'
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return False, 'Erreur lors de la création de l\'utilisateur'
    
    def get_user_by_username(self, username):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error getting user by username: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error getting user by id: {str(e)}")
            return None
    
    def update_user(self, user_id, data):
        try:
            cursor = self.conn.cursor()
            allowed_fields = ['username', 'password', 'role']
            updates = []
            values = []
            
            for field in allowed_fields:
                if field in data and data[field]:
                    if field == 'password':
                        updates.append(f"{field} = %s")
                        values.append(generate_password_hash(data[field]))
                    else:
                        updates.append(f"{field} = %s")
                        values.append(data[field])
            
            if not updates:
                return False, 'Aucune donnée à mettre à jour'
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            
            cursor.execute(query, values)
            self.conn.commit()
            return True, 'Utilisateur mis à jour avec succès'
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return False, 'Erreur lors de la mise à jour de l\'utilisateur'
    
    def delete_user(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            self.conn.commit()
            return True, 'Utilisateur supprimé avec succès'
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False, 'Erreur lors de la suppression de l\'utilisateur'
    
    def list_users(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, username, role FROM users ORDER BY username')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listing users: {str(e)}")
            return []
    
    def change_password(self, user_id, current_password, new_password):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, 'Utilisateur non trouvé'
            
            if not check_password_hash(user['password'], current_password):
                return False, 'Mot de passe actuel incorrect'
            
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE users SET password = %s WHERE id = %s',
                (generate_password_hash(new_password), user_id)
            )
            self.conn.commit()
            return True, 'Mot de passe modifié avec succès'
        except Exception as e:
            print(f"Error changing password: {str(e)}")
            return False, 'Erreur lors du changement de mot de passe'
