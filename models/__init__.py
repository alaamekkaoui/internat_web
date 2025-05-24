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

def create_dummy_data():
    """Create sample data for testing"""
    try:
        # Create sample filieres
        filiere_model = Filiere()
        filieres = [
            "Génie Informatique",
            "Génie Civil",
            "Génie Mécanique",
            "Génie Électrique",
            "Génie Industriel"
        ]
        for filiere in filieres:
            filiere_model.create_filiere(filiere)
        
        # Create sample rooms
        room_model = Room()
        for i in range(1, 21):  # Create 20 rooms
            room_model.create_room(f"Room {i}", random.randint(2, 4))
        
        # Create sample users
        user_model = User()
        users = [
            ("admin", "admin123", "admin"),
            ("user1", "user123", "user"),
            ("user2", "user123", "user")
        ]
        for username, password, role in users:
            user_model.create_user(username, password, role)
        
        # Create sample students
        student_model = Student()
        first_names = ["Mohammed", "Ahmed", "Fatima", "Amina", "Youssef", "Sara", "Karim", "Laila"]
        last_names = ["Alami", "Benani", "Cherkaoui", "Daoudi", "El Fathi", "Hassani", "Idrissi", "Kabbaj"]
        cities = ["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger", "Agadir", "Meknès", "Oujda"]
        
        for _ in range(50):  # Create 50 students
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            cne = f"P{random.randint(100000, 999999)}"
            cin = f"AB{random.randint(100000, 999999)}"
            birth_date = datetime.now() - timedelta(days=random.randint(365*18, 365*25))
            birth_place = random.choice(cities)
            address = f"{random.randint(1, 100)} Rue {random.choice(['Mohammed V', 'Hassan II', 'Ibn Sina', 'Al Massira'])}"
            phone = f"06{random.randint(10000000, 99999999)}"
            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
            filiere_id = random.randint(1, len(filieres))
            academic_year = "2023/2024"
            
            student_model.create_student(
                first_name, last_name, cne, cin, birth_date, birth_place,
                address, phone, email, filiere_id, academic_year
            )
        
        return True
    except Exception as e:
        print(f"Error creating dummy data: {e}")
        return False

