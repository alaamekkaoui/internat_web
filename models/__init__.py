# models/__init__.py
import os
from dotenv import load_dotenv
from models.student import Student
from models.room import Room
from models.filiere import Filiere
from models.user import User
from database.db import get_connection
import pymysql

load_dotenv()

MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB')

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
            try:
                cursor.execute('''
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
                print("Room history table created successfully!")
            except Exception as e:
                print(f"Error creating room_history table: {e}")

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

def reset_database():
    """Reset the entire database by dropping and recreating all tables."""
    conn = get_connection(use_db=False)
    cursor = conn.cursor()
    try:
        # Drop database if exists
        cursor.execute(f"DROP DATABASE IF EXISTS `{MYSQL_DATABASE}`")
        conn.commit()
        
        # Recreate database and tables
        ensure_database_and_tables()
        return True
    except pymysql.Error as e:
        print(f"Error resetting database: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_dummy_data():
    """Create sample data for testing purposes."""
    # Create dummy filieres first
    filiere = Filiere()
    try:
        dummy_filieres = [
            {'name': 'Informatique'},
            {'name': 'Mathématiques'},
            {'name': 'Physique'},
            {'name': 'Chimie'},
            {'name': 'Biologie'}
        ]
        
        for filiere_data in dummy_filieres:
            filiere.add_filiere(filiere_data)
        
        # Create dummy rooms
        room = Room()
        dummy_rooms = [
            {
                'room_number': '101',
                'pavilion': 'A',
                'room_type': 'double',
                'capacity': 2,
                'is_used': False
            },
            {
                'room_number': '102',
                'pavilion': 'A',
                'room_type': 'double',
                'capacity': 2,
                'is_used': False
            },
            {
                'room_number': '201',
                'pavilion': 'B',
                'room_type': 'triple',
                'capacity': 3,
                'is_used': False
            },
            {
                'room_number': '202',
                'pavilion': 'B',
                'room_type': 'single',
                'capacity': 1,
                'is_used': False
            }
        ]
        
        for room_data in dummy_rooms:
            room.add_room(room_data)
        
        # Create dummy students
        student = Student()
        dummy_students = [
            {
                'nom': 'Doe',
                'prenom': 'John',
                'sexe': 'M',
                'matricule': '2024001',
                'cin': 'AB123456',
                'date_naissance': '2000-01-01',
                'nationalite': 'Marocaine',
                'telephone': '0612345678',
                'email': 'john.doe@example.com',
                'annee_universitaire': '2023-2024',
                'filiere_id': '1',  # References Informatique
                'dossier_medicale': 'Aucun',
                'observation': 'Étudiant assidu',
                'laureat': 'non',
                'num_chambre': '101',
                'mobilite': 'non',
                'vie_associative': 'oui',
                'bourse': 'oui',
                'type_section': 'Interne'
            },
            {
                'nom': 'Smith',
                'prenom': 'Jane',
                'sexe': 'F',
                'matricule': '2024002',
                'cin': 'CD789012',
                'date_naissance': '2001-02-15',
                'nationalite': 'Marocaine',
                'telephone': '0623456789',
                'email': 'jane.smith@example.com',
                'annee_universitaire': '2023-2024',
                'filiere_id': '2',  # References Mathématiques
                'dossier_medicale': 'Aucun',
                'observation': 'Étudiante brillante',
                'laureat': 'oui',
                'num_chambre': '102',
                'mobilite': 'non',
                'vie_associative': 'oui',
                'bourse': 'oui',
                'type_section': 'Interne'
            }
        ]

        for student_data in dummy_students:
            student.add_student(student_data)
            
        print("Dummy data created successfully!")
        return True
    except Exception as e:
        print(f"Error creating dummy data: {e}")
        return False

def create_default_admin_user_if_not_exists():
    # Import User model locally to avoid circular import issues if any
    from models.user import User 
    admin_user = User.find_by_username('admin')
    if not admin_user:
        admin_user_obj = User()
        # Use a more secure password in a real application
        created_user = admin_user_obj.create(username='admin', password='admin', role='admin')
        if created_user and created_user.id:
            print("Default admin user created successfully.")
        else:
            print("Failed to create default admin user. Check logs for errors.")
    else:
        print("Admin user already exists.")

