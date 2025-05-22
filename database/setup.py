import sqlite3
import os
from models.user import User
from dotenv import load_dotenv
from database.db import get_connection
import pymysql

load_dotenv()

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB', 'internat')

def get_connection(use_db=True):
    """Get a connection to the MySQL database"""
    try:
        if use_db:
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        else:
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        return conn
    except pymysql.Error as e:
        print(f"Error connecting to database: {e}")
        raise e

def create_tables():
    """Create all necessary tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            matricule TEXT UNIQUE NOT NULL,
            cin TEXT UNIQUE NOT NULL,
            date_naissance DATE NOT NULL,
            nationalite TEXT NOT NULL,
            sexe TEXT NOT NULL,
            telephone TEXT NOT NULL,
            email TEXT,
            annee_universitaire TEXT NOT NULL,
            filiere_id INTEGER,
            dossier_medicale TEXT,
            observation TEXT,
            laureat TEXT NOT NULL,
            num_chambre TEXT,
            mobilite TEXT NOT NULL,
            vie_associative TEXT NOT NULL,
            bourse TEXT NOT NULL,
            photo TEXT,
            type_section TEXT NOT NULL,
            FOREIGN KEY (filiere_id) REFERENCES filieres (id)
        )
    ''')

    # Create filieres table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filieres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    # Create rooms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            pavilion TEXT NOT NULL,
            room_type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            is_used BOOLEAN DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

def reset_database():
    """Force drop and recreate the database"""
    conn = None
    cursor = None
    try:
        print("DEBUG: Resetting database...")
        # First connect without database
        conn = get_connection(use_db=False)
        cursor = conn.cursor()
        
        # Kill all connections to the database
        print(f"DEBUG: Killing all connections to {MYSQL_DATABASE}...")
        cursor.execute(f"""
            SELECT CONCAT('KILL ', id, ';')
            FROM information_schema.processlist
            WHERE db = '{MYSQL_DATABASE}';
        """)
        kill_commands = cursor.fetchall()
        for cmd in kill_commands:
            try:
                cursor.execute(list(cmd.values())[0])
            except:
                pass
        
        # Drop database if exists
        print(f"DEBUG: Dropping database {MYSQL_DATABASE}...")
        cursor.execute(f"DROP DATABASE IF EXISTS `{MYSQL_DATABASE}`")
        print(f"DEBUG: Dropped database {MYSQL_DATABASE}")
        
        # Create database
        print(f"DEBUG: Creating database {MYSQL_DATABASE}...")
        cursor.execute(f"CREATE DATABASE `{MYSQL_DATABASE}` DEFAULT CHARACTER SET 'utf8mb4'")
        print(f"DEBUG: Created database {MYSQL_DATABASE}")
        
        # Select the database
        conn.select_db(MYSQL_DATABASE)
        
        # Create tables
        ensure_database_and_tables()
        
        conn.commit()
        print("DEBUG: Database reset completed successfully")
        return True
    except Exception as e:
        print(f"DEBUG: Error resetting database: {str(e)}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def ensure_database_and_tables():
    """Ensure database and tables exist"""
    conn = None
    cursor = None
    try:
        # First connect without database
        conn = get_connection(use_db=False)
        cursor = conn.cursor()
        
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

        # Create filieres table first (no foreign keys)
        if 'filieres' not in existing_tables:
            print("Creating filieres table...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS filieres (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
            print("Filieres table created successfully!")

        # Create rooms table (no foreign keys)
        if 'rooms' not in existing_tables:
            print("Creating rooms table...")
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

        # Create users table (no foreign keys)
        if 'users' not in existing_tables:
            print("Creating users table...")
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

        # Create students table (depends on filieres)
        if 'students' not in existing_tables:
            print("Creating students table...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                prenom VARCHAR(255) NOT NULL,
                matricule VARCHAR(50) UNIQUE NOT NULL,
                cin VARCHAR(50) UNIQUE NOT NULL,
                date_naissance DATE NOT NULL,
                nationalite VARCHAR(100) NOT NULL,
                sexe ENUM('M', 'F') NOT NULL,
                telephone VARCHAR(20) NOT NULL,
                email VARCHAR(255),
                annee_universitaire VARCHAR(20) NOT NULL,
                filiere_id BIGINT UNSIGNED,
                dossier_medicale TEXT,
                observation TEXT,
                laureat VARCHAR(100) NOT NULL,
                num_chambre VARCHAR(20),
                mobilite VARCHAR(100) NOT NULL,
                vie_associative TEXT NOT NULL,
                bourse VARCHAR(100) NOT NULL,
                photo VARCHAR(255),
                type_section VARCHAR(50) NOT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (filiere_id) REFERENCES filieres(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
            print("Students table created successfully!")

        conn.commit()
        print("All tables checked and created successfully!")
        
    except pymysql.Error as e:
        print(f"Error creating database/tables: {e}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    ensure_database_and_tables() 