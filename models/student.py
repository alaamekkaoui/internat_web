from werkzeug.utils import secure_filename
import os
import uuid
from database.db import get_connection, execute_query
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
        """Get all students with their filiere information"""
        query = """
        SELECT s.*, f.name as filiere_name 
        FROM students s 
        LEFT JOIN filieres f ON s.filiere_id = f.id 
        ORDER BY s.created_at DESC
        """
        return execute_query(query)

    def get_student(self, student_id):
        """Alias for get_student_by_id for backward compatibility"""
        return self.get_student_by_id(student_id)

    def get_student_by_id(self, student_id):
        """Get a student by ID"""
        query = """
        SELECT s.*, f.name as filiere_name 
        FROM students s 
        LEFT JOIN filieres f ON s.filiere_id = f.id 
        WHERE s.id = %s
        """
        result = execute_query(query, (student_id,))
        return result[0] if result else None

    def create_student(self, student_data):
        """Create a new student"""
        query = """
        INSERT INTO students (
            nom, prenom, matricule, cin, date_naissance, nationalite,
            sexe, telephone, email, annee_universitaire, filiere_id,
            dossier_medicale, observation, laureat, num_chambre,
            mobilite, vie_associative, bourse, photo, type_section
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        params = (
            student_data['nom'], student_data['prenom'], student_data['matricule'],
            student_data['cin'], student_data['date_naissance'], student_data['nationalite'],
            student_data['sexe'], student_data['telephone'], student_data['email'],
            student_data['annee_universitaire'], student_data.get('filiere_id'),
            student_data.get('dossier_medicale'), student_data.get('observation'),
            student_data['laureat'], student_data.get('num_chambre'),
            student_data['mobilite'], student_data['vie_associative'],
            student_data['bourse'], student_data.get('photo'),
            student_data['type_section']
        )
        return execute_query(query, params, fetch=False)

    def update_student(self, student_id, student_data):
        """Update a student"""
        query = """
        UPDATE students SET
            nom = %s, prenom = %s, matricule = %s, cin = %s,
            date_naissance = %s, nationalite = %s, sexe = %s,
            telephone = %s, email = %s, annee_universitaire = %s,
            filiere_id = %s, dossier_medicale = %s, observation = %s,
            laureat = %s, num_chambre = %s, mobilite = %s,
            vie_associative = %s, bourse = %s, photo = %s,
            type_section = %s
        WHERE id = %s
        """
        params = (
            student_data['nom'], student_data['prenom'], student_data['matricule'],
            student_data['cin'], student_data['date_naissance'], student_data['nationalite'],
            student_data['sexe'], student_data['telephone'], student_data['email'],
            student_data['annee_universitaire'], student_data.get('filiere_id'),
            student_data.get('dossier_medicale'), student_data.get('observation'),
            student_data['laureat'], student_data.get('num_chambre'),
            student_data['mobilite'], student_data['vie_associative'],
            student_data['bourse'], student_data.get('photo'),
            student_data['type_section'], student_id
        )
        return execute_query(query, params, fetch=False)

    def delete_student(self, student_id):
        """Delete a student"""
        query = "DELETE FROM students WHERE id = %s"
        return execute_query(query, (student_id,), fetch=False)

    def get_students_by_filiere(self, filiere_id):
        """Get all students in a specific filiere"""
        query = """
        SELECT s.*, f.name as filiere_name 
        FROM students s 
        LEFT JOIN filieres f ON s.filiere_id = f.id 
        WHERE s.filiere_id = %s 
        ORDER BY s.created_at DESC
        """
        return execute_query(query, (filiere_id,))

    def get_students_by_room(self, room_number):
        """Get all students in a specific room"""
        query = """
        SELECT s.*, f.name as filiere_name 
        FROM students s 
        LEFT JOIN filieres f ON s.filiere_id = f.id 
        WHERE s.num_chambre = %s 
        ORDER BY s.created_at DESC
        """
        return execute_query(query, (room_number,))

    def update_student_image(self, student_id, filename):
        """Update a student's photo filename"""
        query = "UPDATE students SET photo = %s WHERE id = %s"
        return execute_query(query, (filename, student_id), fetch=False)

    def search_students(self, keyword=None, chambre=None):
        """Search students by keyword or room number"""
        query = """
        SELECT s.*, f.name as filiere_name 
        FROM students s 
        LEFT JOIN filieres f ON s.filiere_id = f.id 
        WHERE 1=1
        """
        params = []

        if keyword:
            query += " AND (s.nom LIKE %s OR s.prenom LIKE %s OR s.matricule LIKE %s)"
            keyword_param = f"%{keyword}%"
            params.extend([keyword_param, keyword_param, keyword_param])

        if chambre:
            query += " AND s.num_chambre = %s"
            params.append(chambre)

        query += " ORDER BY s.created_at DESC"
        return execute_query(query, params)

    def count_students(self):
        """Count the total number of students"""
        query = "SELECT COUNT(*) as count FROM students"
        result = execute_query(query)
        return result[0]['count'] if result else 0

    def count_gender(self):
        """Count the number of male and female students"""
        query = "SELECT sexe, COUNT(*) as count FROM students GROUP BY sexe"
        results = execute_query(query)
        return {row['sexe']: row['count'] for row in results}
