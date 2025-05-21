from werkzeug.utils import secure_filename
import os
import uuid
from database.db import get_connection
import pymysql
from database.setup import ensure_database_and_tables
from datetime import datetime

class Student:
    def __init__(self):
        self.table_name = 'students'
        self.conn = get_connection()
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def get_all_students(self):
        """Get all students with their filiere names."""
        try:
            query = """
                SELECT s.*, f.name as filiere_name 
                FROM students s 
                LEFT JOIN filieres f ON s.filiere_id = f.id 
                ORDER BY s.nom, s.prenom
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except pymysql.Error as e:
            print(f"Database error in get_all_students: {e}")
            raise Exception(str(e))

    def get_student(self, student_id):
        """Get a student by ID."""
        try:
            self.cursor.execute(f"""
                SELECT s.*, f.name as filiere_name 
                FROM {self.table_name} s 
                LEFT JOIN filieres f ON s.filiere_id = f.id 
                WHERE s.id = %s
            """, (student_id,))
            return self.cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error getting student by ID: {e}")
            return None

    def add_student(self, data):
        """Add a new student to the database."""
        try:
            # Set default values for optional fields
            if 'dossier_medicale' not in data or not data['dossier_medicale']:
                data['dossier_medicale'] = 'non'
            if 'bourse' not in data or not data['bourse']:
                data['bourse'] = 'non'

            # Convert date_naissance to proper format if it's a string
            if 'date_naissance' in data and isinstance(data['date_naissance'], str):
                try:
                    # Parse the date string
                    date_obj = datetime.strptime(data['date_naissance'], '%Y-%m-%d')
                    # Format it back to string in MySQL format
                    data['date_naissance'] = date_obj.strftime('%Y-%m-%d')
                except ValueError as e:
                    raise Exception(f"Invalid date format for date_naissance: {data['date_naissance']}")

            # Prepare the SQL query
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
            
            # Execute the query
            self.cursor.execute(query, list(data.values()))
            self.conn.commit()
            return self.cursor.lastrowid
        except pymysql.Error as e:
            self.conn.rollback()
            raise Exception(str(e))
        except Exception as e:
            self.conn.rollback()
            raise Exception(str(e))

    def update_student(self, student_id, data):
        """Update a student's information."""
        try:
            # Map form fields to database fields
            student_data = {
                'nom': data.get('nom') or data.get('lastname'),
                'prenom': data.get('prenom') or data.get('firstname'),
                'sexe': data.get('sexe') or data.get('gender'),
                'matricule': data.get('matricule'),
                'cin': data.get('cin'),
                'date_naissance': data.get('date_naissance') or data.get('birth_date'),
                'nationalite': data.get('nationalite') or data.get('nationality'),
                'telephone': data.get('telephone') or data.get('phone'),
                'email': data.get('email'),
                'annee_universitaire': data.get('annee_universitaire') or data.get('academic_year'),
                'filiere_id': data.get('filiere_id'),
                'dossier_medicale': data.get('dossier_medicale') or data.get('medical_record'),
                'observation': data.get('observation'),
                'photo': data.get('photo'),
                'laureat': data.get('laureat'),
                'num_chambre': data.get('num_chambre') or data.get('room_number'),
                'mobilite': data.get('mobilite'),
                'vie_associative': data.get('vie_associative'),
                'bourse': data.get('bourse'),
                'type_section': data.get('type_section')
            }

            # Remove None values
            student_data = {k: v for k, v in student_data.items() if v is not None}

            # Convert date_naissance to proper format if it's a string
            if 'date_naissance' in student_data and isinstance(student_data['date_naissance'], str):
                try:
                    # Parse the date string
                    date_obj = datetime.strptime(student_data['date_naissance'], '%Y-%m-%d')
                    # Format it back to string in MySQL format
                    student_data['date_naissance'] = date_obj.strftime('%Y-%m-%d')
                except ValueError as e:
                    raise Exception(f"Invalid date format for date_naissance: {student_data['date_naissance']}")

            # Prepare the SQL query
            set_clause = ', '.join([f"{field} = %s" for field in student_data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
            
            # Execute the query
            values = list(student_data.values())
            values.append(student_id)
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except pymysql.Error as e:
            print(f"Error updating student: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def delete_student(self, student_id):
        """Delete a student from the database."""
        try:
            self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (student_id,))
            self.conn.commit()
            return True
        except pymysql.Error as e:
            print(f"Error deleting student: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def update_student_image(self, student_id, filename):
        """Update a student's photo filename."""
        try:
            # First check if student exists
            self.cursor.execute(f"SELECT id FROM {self.table_name} WHERE id = %s", (student_id,))
            if not self.cursor.fetchone():
                raise Exception("Student not found")

            # Update the photo field
            self.cursor.execute(f"UPDATE {self.table_name} SET photo = %s WHERE id = %s", (filename, student_id))
            self.conn.commit()
            return True
        except pymysql.Error as e:
            print(f"Error updating student image: {e}")
            self.conn.rollback()
            raise Exception(str(e))
        except Exception as e:
            print(f"Error in update_student_image: {e}")
            self.conn.rollback()
            raise Exception(str(e))

    def search_students(self, keyword=None, chambre=None):
        """Search students by keyword or room number."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = []

            if keyword:
                query += " AND (nom LIKE %s OR prenom LIKE %s OR matricule LIKE %s)"
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param, keyword_param])

            if chambre:
                query += " AND num_chambre = %s"
                params.append(chambre)

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error searching students: {e}")
            return []

    def count_students(self):
        """Count the total number of students in the system."""
        try:
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name}")
            result = self.cursor.fetchone()
            return result['count'] if result else 0
        except pymysql.Error as e:
            print(f"Error counting students: {e}")
            return 0

    def count_gender(self):
        """Count the number of male and female students."""
        try:
            self.cursor.execute(f"SELECT sexe, COUNT(*) as count FROM {self.table_name} GROUP BY sexe")
            results = self.cursor.fetchall()
            return {row['sexe']: row['count'] for row in results}
        except pymysql.Error as e:
            print(f"Error counting gender: {e}")
            return {}
