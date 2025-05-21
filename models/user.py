import pymysql
from database.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id=None, username=None, password=None, role=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def create(self, username, password, role='user'):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (self.username, self.password, self.role)
            )
            self.conn.commit()
            self.id = self.cursor.lastrowid
            return self
        except pymysql.Error as e:
            print(f"Error creating user: {e}")
            self.conn.rollback()
            return None

    @staticmethod
    def find_by_username(username):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            if user_data:
                # Ensure all expected keys are present
                expected_keys = ['id', 'username', 'password', 'role']
                if all(key in user_data for key in expected_keys):
                    return User(id=user_data['id'], username=user_data['username'], password=user_data['password'], role=user_data['role'])
                else:
                    print(f"User data for {username} is missing keys: {user_data}")
                    return None
            return None
        except pymysql.Error as e:
            print(f"Error finding user by username: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_by_id(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                 # Ensure all expected keys are present
                expected_keys = ['id', 'username', 'password', 'role']
                if all(key in user_data for key in expected_keys):
                    return User(id=user_data['id'], username=user_data['username'], password=user_data['password'], role=user_data['role'])
                else:
                    print(f"User data for id {user_id} is missing keys: {user_data}")
                    return None
            return None
        except pymysql.Error as e:
            print(f"Error finding user by id: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
