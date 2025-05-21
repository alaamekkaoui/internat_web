# models/filiere.py

from database.db import get_connection
from datetime import datetime

class Filiere:
    def __init__(self):
        self.table_name = 'filieres'
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def get_all_filieres(self):
        """Get all filieres from the database."""
        try:
            self.cursor.execute(f"SELECT * FROM {self.table_name}")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all filieres: {e}")
            return []

    def get_filiere(self, filiere_id):
        try:
            self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = %s", (filiere_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting filiere by ID: {e}")
            return None

    def add_filiere(self, data):
        try:
            name = data.get('name') if isinstance(data, dict) else data
            print(f"add_filiere called with: {data} (parsed name: {name})")
            if not name or name.lower() == 'name':
                raise Exception('Missing or invalid field: name')
            query = f"INSERT INTO {self.table_name} (name) VALUES (%s)"
            print(f"Executing SQL: {query} with value: {name}")
            self.cursor.execute(query, (name,))
            self.conn.commit()
            print(f"Inserted filiere with name: {name}")
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Database error in add_filiere: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def update_filiere(self, filiere_id, data):
        try:
            name = data.get('name') if isinstance(data, dict) else data
            if not name or name.lower() == 'name':
                raise Exception('Missing or invalid field: name')
            query = f"UPDATE {self.table_name} SET name = %s WHERE id = %s"
            self.cursor.execute(query, (name, filiere_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating filiere: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def delete_filiere(self, filiere_id):
        try:
            self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (filiere_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting filiere: {e}")
            self.conn.rollback()
            raise Exception(str(e))


