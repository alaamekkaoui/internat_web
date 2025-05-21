import sqlite3
from werkzeug.security import generate_password_hash
from database.db import get_connection

def dict_factory(cursor, row):
    """Convert database row objects to a dictionary"""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class User:
    def __init__(self):
        self.table_name = 'users'

    def create_table(self):
        try:
            print("DEBUG: Creating users table")
            conn = get_connection()
            cursor = conn.cursor()
            
            # Drop existing table to ensure clean state
            cursor.execute('DROP TABLE IF EXISTS users')
            
            # Create table with correct structure
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
            # Verify table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("DEBUG: Table structure:", columns)
            
            conn.close()
            print("DEBUG: Table created successfully")
        except Exception as e:
            print(f"DEBUG: Error creating table: {str(e)}")
            raise e

    def get_user_by_username(self, username):
        try:
            print(f"DEBUG: Getting user by username: {username}")
            conn = get_connection()
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            query = 'SELECT * FROM users WHERE username = ?'
            params = (username,)
            print(f"DEBUG: Query: {query}")
            print(f"DEBUG: Params: {params}")
            cursor.execute(query, params)
            user = cursor.fetchone()
            print(f"DEBUG: Result: {user}")
            return user
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return None
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        try:
            print(f"DEBUG: Getting user by id: {user_id}")
            conn = get_connection()
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            query = 'SELECT * FROM users WHERE id = ?'
            params = (user_id,)
            print(f"DEBUG: Query: {query}")
            print(f"DEBUG: Params: {params}")
            cursor.execute(query, params)
            user = cursor.fetchone()
            print(f"DEBUG: Result: {user}")
            return user
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return None
        finally:
            conn.close()

    def create_user(self, username, password, role='user'):
        try:
            print(f"DEBUG: Creating user with username: {username}, role: {role}")
            conn = get_connection()
            cursor = conn.cursor()
            
            # Verify table structure before insert
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("DEBUG: Current table structure:", columns)
            
            query = 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)'
            params = (username, password, role)
            print(f"DEBUG: Query: {query}")
            print(f"DEBUG: Params: {params}")
            
            cursor.execute(query, params)
            conn.commit()
            print("DEBUG: User created successfully")
            return True
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return False
        finally:
            conn.close()

    def update_password(self, user_id, new_password):
        try:
            print(f"DEBUG: Updating password for user_id: {user_id}")
            conn = get_connection()
            cursor = conn.cursor()
            query = 'UPDATE users SET password = ? WHERE id = ?'
            params = (new_password, user_id)
            print(f"DEBUG: Query: {query}")
            print(f"DEBUG: Params: {params}")
            cursor.execute(query, params)
            conn.commit()
            print("DEBUG: Password updated successfully")
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du mot de passe: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return False
        finally:
            conn.close()

    def update_user(self, user_id, role=None):
        try:
            print(f"DEBUG: Updating user {user_id} with role: {role}")
            conn = get_connection()
            cursor = conn.cursor()
            
            if role is not None:
                query = 'UPDATE users SET role = ? WHERE id = ?'
                params = (role, user_id)
                print(f"DEBUG: Query: {query}")
                print(f"DEBUG: Params: {params}")
                cursor.execute(query, params)
                conn.commit()
                print("DEBUG: User updated successfully")
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return False
        finally:
            conn.close()

    def delete_user(self, user_id):
        try:
            print(f"DEBUG: Deleting user {user_id}")
            conn = get_connection()
            cursor = conn.cursor()
            query = 'DELETE FROM users WHERE id = ?'
            params = (user_id,)
            print(f"DEBUG: Query: {query}")
            print(f"DEBUG: Params: {params}")
            cursor.execute(query, params)
            conn.commit()
            print("DEBUG: User deleted successfully")
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de l'utilisateur: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return False
        finally:
            conn.close()

    def get_all_users(self):
        try:
            print("DEBUG: Getting all users")
            conn = get_connection()
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            query = 'SELECT * FROM users'
            print(f"DEBUG: Query: {query}")
            cursor.execute(query)
            users = cursor.fetchall()
            print(f"DEBUG: Found {len(users)} users")
            return users
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return []
        finally:
            conn.close()

    def create_default_admin(self):
        """Create a default admin user if no users exist"""
        try:
            print("DEBUG: Checking if default admin needs to be created")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            conn.close()
            print(f"DEBUG: Found {count} existing users")

            if count == 0:
                print("DEBUG: Creating default admin user")
                hashed_password = generate_password_hash('admin123')
                result = self.create_user(
                    username='admin',
                    password=hashed_password,
                    role='admin'
                )
                print(f"DEBUG: Default admin creation result: {result}")
                return result
            return False
        except Exception as e:
            print(f"Erreur lors de la création de l'admin par défaut: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return False
