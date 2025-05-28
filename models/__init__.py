# models/__init__.py
import os
from dotenv import load_dotenv
from models.student import Student
from models.room import Room
from models.filiere import Filiere
from models.user import User
from models.room_history import RoomHistory
from database.db import get_connection
import pymysql
from datetime import datetime, timedelta
import random

load_dotenv()

MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB') or os.environ.get('MYSQL_NAME')

def ensure_database_and_tables():
    # First connect without database
    conn = get_connection(use_db=False)
    cursor = conn.cursor()
    
    try:
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` DEFAULT CHARACTER SET 'utf8mb4'")
        conn.commit()
        
        # Now connect to the database
        conn.select_db(MYSQL_DATABASE)
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        # Get the first column name from the result
        if tables and len(tables) > 0:
            first_key = list(tables[0].keys())[0]
            existing_tables = [table[first_key] for table in tables]
        else:
            existing_tables = []
        
        # Create students table if not exists
        if 'students' not in existing_tables:
            print("Creating students table...")
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    prenom VARCHAR(255) NOT NULL,
                    sexe ENUM('M','F') DEFAULT NULL,
                    matricule VARCHAR(255) NOT NULL,
                    cin VARCHAR(255) NOT NULL,
                    date_naissance DATE NOT NULL,
                    nationalite VARCHAR(255) NOT NULL,
                    telephone VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    annee_universitaire VARCHAR(255) NOT NULL,
                    filiere_id VARCHAR(255) NOT NULL,
                    dossier_medicale TEXT NOT NULL,
                    observation TEXT DEFAULT NULL,
                    photo VARCHAR(255) DEFAULT NULL,
                    laureat VARCHAR(255) DEFAULT NULL,
                    num_chambre VARCHAR(255) DEFAULT NULL,
                    mobilite VARCHAR(255) DEFAULT NULL,
                    vie_associative VARCHAR(255) DEFAULT NULL,
                    bourse VARCHAR(255) NOT NULL,
                    type_section VARCHAR(32) DEFAULT 'Interne',
                    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                print("Students table created successfully!")
            except Exception as e:
                print(f"Error creating students table: {e}")

        # Create rooms table if not exists
        if 'rooms' not in existing_tables:
            print("Creating rooms table...")
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS rooms (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    room_number VARCHAR(32) NOT NULL,
                    pavilion VARCHAR(64) NOT NULL,
                    room_type ENUM('single','double','triple') NOT NULL,
                    capacity INT NOT NULL,
                    is_used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                print("Rooms table created successfully!")
            except Exception as e:
                print(f"Error creating rooms table: {e}")

        # Create filieres table if not exists
        if 'filieres' not in existing_tables:
            print("Creating filieres table...")
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS filieres (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                print("Filieres table created successfully!")
            except Exception as e:
                print(f"Error creating filieres table: {e}")

        # Create room_history table if not exists
        if 'room_history' not in existing_tables:
            print("Creating room_history table...")
            print('''
            CREATE TABLE IF NOT EXISTS room_history (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                student_id BIGINT UNSIGNED NOT NULL,
                room_id BIGINT UNSIGNED NOT NULL,
                year VARCHAR(16) NOT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
            
        # Create users table if not exists
        if 'users' not in existing_tables:
            print("Creating users table...")
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                print("Users table created successfully!")
            except Exception as e:
                print(f"Error creating users table: {e}")
        conn.commit()
        print("All tables checked and created successfully!")
        
    except pymysql.Error as e:
        print(f"Error creating database/tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def create_dummy_data():
    from models.student import Student
    from models.room import Room
    from models.filiere import Filiere
    from models.user import User
    import random
    from datetime import datetime

    # Add sample filieres
    filiere_model = Filiere()
    filiere_names = ['Informatique', 'Agronomie', 'Génie Rural']
    filiere_ids = []
    for name in filiere_names:
        filiere = filiere_model.add_filiere({'name': name})
        filiere_ids.append(filiere['id'] if isinstance(filiere, dict) and 'id' in filiere else filiere_model.cursor.lastrowid)

    # Add sample rooms
    room_model = Room()
    rooms = [
        {'room_number': 'A101', 'pavilion': 'A', 'room_type': 'single', 'capacity': 1},
        {'room_number': 'B202', 'pavilion': 'B', 'room_type': 'double', 'capacity': 2},
        {'room_number': 'C303', 'pavilion': 'C', 'room_type': 'triple', 'capacity': 3},
    ]
    for room in rooms:
        room_model.add_room(room)

    # Add sample students
    student_model = Student()
    students = [
        {'nom': 'Dupont', 'prenom': 'Jean', 'matricule': 'STU001', 'sexe': 'M', 'cin': 'CIN000001', 'date_naissance': '2000-01-01', 'nationalite': 'Marocaine', 'telephone': '0600000001', 'email': 'jean.dupont@example.com', 'annee_universitaire': f'{datetime.now().year}/{datetime.now().year+1}', 'filiere_id': filiere_ids[0], 'num_chambre': 'A101', 'type_section': 'IAV'},
        {'nom': 'Martin', 'prenom': 'Marie', 'matricule': 'STU002', 'sexe': 'F', 'cin': 'CIN000002', 'date_naissance': '2001-02-02', 'nationalite': 'Marocaine', 'telephone': '0600000002', 'email': 'marie.martin@example.com', 'annee_universitaire': f'{datetime.now().year}/{datetime.now().year+1}', 'filiere_id': filiere_ids[1], 'num_chambre': 'B202', 'type_section': 'APESA'},
        {'nom': 'Bernard', 'prenom': 'Pierre', 'matricule': 'STU003', 'sexe': 'M', 'cin': 'CIN000003', 'date_naissance': '2002-03-03', 'nationalite': 'Marocaine', 'telephone': '0600000003', 'email': 'pierre.bernard@example.com', 'annee_universitaire': f'{datetime.now().year}/{datetime.now().year+1}', 'filiere_id': filiere_ids[2], 'num_chambre': 'C303', 'type_section': 'IAV'},
    ]
    for student in students:
        student_model.create_student(student)

    # Add default admin user
    user_model = User()
    if not user_model.get_user_by_username('admin'):
        user_model.create_user({'username': 'admin', 'password': 'admin', 'role': 'admin'})
