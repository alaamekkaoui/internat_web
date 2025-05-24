from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import pymysql

from database.db import get_connection
from database.setup import ensure_database_and_tables

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
        try:
            self.cursor.execute("""
                SELECT s.*, f.name as filiere_name
                FROM students s
                LEFT JOIN filieres f ON s.filiere_id = f.id
                ORDER BY s.created_at DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] get_all_students: {e}")
            return []

    def get_student_by_id(self, student_id):
        try:
            self.cursor.execute("""
                SELECT s.*, f.name as filiere_name, r.room_number, r.pavilion, r.room_type, r.capacity
                FROM students s
                LEFT JOIN filieres f ON s.filiere_id = f.id
                LEFT JOIN rooms r ON s.num_chambre = r.room_number
                WHERE s.id = %s
            """, (student_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"[ERROR] get_student_by_id: {e}")
            return None

    def get_student(self, student_id):
        return self.get_student_by_id(student_id)

    def create_student(self, student_data):
        required = ['nom', 'matricule', 'sexe']
        for field in required:
            if not student_data.get(field):
                raise Exception(f"Le champ {field} est obligatoire.")

        # Calculate academic year based on current year
        current_year = datetime.now().year
        next_year = current_year + 1
        default_academic_year = f"{current_year}/{next_year}"

        defaults = {
            'prenom': 'Non trouvé', 'cin': 'Non trouvé', 'date_naissance': '0001-01-01',
            'nationalite': 'Non trouvé', 'telephone': 'Non trouvé', 'email': 'Non trouvé',
            'annee_universitaire': default_academic_year, 'filiere_id': None,
            'dossier_medicale': 'Non trouvé', 'observation': '', 'laureat': 'non',
            'num_chambre': None, 'mobilite': 'non', 'vie_associative': 'non',
            'bourse': 'non', 'photo': None, 'type_section': 'Interne'
        }
        for k, v in defaults.items():
            if not student_data.get(k):
                student_data[k] = v

        # Convert any NaN values to None (for Excel import)
        import math
        for k, v in student_data.items():
            if isinstance(v, float) and math.isnan(v):
                student_data[k] = None
            elif isinstance(v, str) and v.strip().lower() == 'nan':
                student_data[k] = None

        # Ensure filiere_id is None if missing or empty
        if not student_data.get('filiere_id') or str(student_data.get('filiere_id')).strip() in ('', 'None', 'none', 'null'):
            student_data['filiere_id'] = None

        query = """
        INSERT INTO students (
            nom, prenom, matricule, cin, date_naissance, nationalite,
            sexe, telephone, email, annee_universitaire, filiere_id,
            dossier_medicale, observation, laureat, num_chambre,
            mobilite, vie_associative, bourse, photo, type_section
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = tuple(student_data[k] for k in [
            'nom', 'prenom', 'matricule', 'cin', 'date_naissance', 'nationalite', 'sexe',
            'telephone', 'email', 'annee_universitaire', 'filiere_id', 'dossier_medicale',
            'observation', 'laureat', 'num_chambre', 'mobilite', 'vie_associative', 'bourse',
            'photo', 'type_section'])

        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            student_id = self.cursor.lastrowid
            
            # Update room status if a room is assigned
            if student_data.get('num_chambre'):
                from models.room import Room
                Room().set_room_used_status(student_data['num_chambre'])
                
            return student_id
        except Exception as e:
            print(f"[ERROR] create_student: {e}")
            self.conn.rollback()
            return None

    def add_student(self, student_data):
        return self.create_student(student_data)

    def update_student(self, student_id, student_data):
        allowed_fields = [
            'nom', 'prenom', 'matricule', 'cin', 'date_naissance', 'nationalite', 'sexe',
            'telephone', 'email', 'annee_universitaire', 'filiere_id', 'dossier_medicale',
            'observation', 'laureat', 'num_chambre', 'mobilite', 'vie_associative',
            'bourse', 'photo', 'type_section'
        ]
        for field in allowed_fields:
            student_data.setdefault(field, None)

        if student_data.get('num_chambre') == '':
            student_data['num_chambre'] = None

        # Calculate academic year based on current year
        current_year = datetime.now().year
        next_year = current_year + 1
        student_data['annee_universitaire'] = f"{current_year}/{next_year}"

        try:
            # Get previous room before update
            self.cursor.execute("SELECT num_chambre FROM students WHERE id = %s", (student_id,))
            prev_room = self.cursor.fetchone()
            prev_room_number = prev_room['num_chambre'] if prev_room and isinstance(prev_room, dict) else None

            query = """
            UPDATE students SET
                nom = %s, prenom = %s, matricule = %s, cin = %s,
                date_naissance = %s, nationalite = %s, sexe = %s,
                telephone = %s, email = %s, annee_universitaire = %s,
                filiere_id = %s, dossier_medicale = %s, observation = %s,
                laureat = %s, num_chambre = %s, mobilite = %s,
                vie_associative = %s, bourse = %s, photo = %s,
                type_section = %s WHERE id = %s
            """

            params = tuple(student_data[k] for k in allowed_fields) + (student_id,)
            self.cursor.execute(query, params)
            self.conn.commit()

            # After update, recalculate room usage for both previous and new room
            from models.room import Room
            room_model = Room()
            
            # Update previous room status if it exists and is different from new room
            if prev_room_number and prev_room_number != student_data.get('num_chambre'):
                room_model.set_room_used_status(prev_room_number)
            
            # Update new room status if it exists
            if student_data.get('num_chambre'):
                room_model.set_room_used_status(student_data['num_chambre'])
            
            return True
        except Exception as e:
            print(f"[ERROR] update_student: {repr(e)} (type: {type(e)})")
            print(f"[DEBUG] update_student params: {params}")
            self.conn.rollback()
            return {'error': f'{repr(e)} (type: {type(e)})'}

    def delete_student(self, student_id):
        try:
            # Get student's room before deletion
            self.cursor.execute("SELECT num_chambre FROM students WHERE id = %s", (student_id,))
            student = self.cursor.fetchone()
            room_number = student['num_chambre'] if student and isinstance(student, dict) else None

            # Delete the student
            self.cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            self.conn.commit()

            # Update room status if student had a room
            if room_number:
                from models.room import Room
                Room().set_room_used_status(room_number)

            return True
        except Exception as e:
            error_msg = f"[ERROR] delete_student: {repr(e)} (type: {type(e)})"
            print(error_msg)
            self.conn.rollback()
            return {'error': error_msg}

    def get_students_by_filiere(self, filiere_id):
        try:
            self.cursor.execute("""
                SELECT s.*, f.name as filiere_name
                FROM students s
                LEFT JOIN filieres f ON s.filiere_id = f.id
                WHERE s.filiere_id = %s
                ORDER BY s.created_at DESC
            """, (filiere_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] get_students_by_filiere: {e}")
            return []

    def get_students_by_room(self, room_number):
        try:
            self.cursor.execute("""
                SELECT s.*, f.name as filiere_name
                FROM students s
                LEFT JOIN filieres f ON s.filiere_id = f.id
                WHERE s.num_chambre = %s
                ORDER BY s.created_at DESC
            """, (room_number,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[ERROR] get_students_by_room: {e}")
            return []
