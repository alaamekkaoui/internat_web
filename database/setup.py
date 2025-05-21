import os
from dotenv import load_dotenv
from database.db import get_connection
import pymysql

load_dotenv()

def migrate_database():
    """Migrate the database structure to the latest version."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if filiere_niveau_etud column exists
        cursor.execute("SHOW COLUMNS FROM students LIKE 'filiere_niveau_etud'")
        if cursor.fetchone():
            print("Migrating students table...")
            # Add new filiere_id column
            cursor.execute("""
                ALTER TABLE students 
                ADD COLUMN filiere_id BIGINT UNSIGNED AFTER annee_universitaire,
                ADD FOREIGN KEY (filiere_id) REFERENCES filieres(id)
            """)
            
            # Copy data from filiere_niveau_etud to filiere_id
            cursor.execute("""
                UPDATE students s
                INNER JOIN filieres f ON f.name = s.filiere_niveau_etud
                SET s.filiere_id = f.id
            """)
            
            # Drop the old column
            cursor.execute("ALTER TABLE students DROP COLUMN filiere_niveau_etud")
            
            print("Migration completed successfully!")
        
        conn.commit()
        return True
    except pymysql.Error as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def ensure_database_and_tables():
    conn = get_connection()
    cursor = conn.cursor()
    DB_NAME = os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB')
    
    try:
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET 'utf8mb4'")
        conn.select_db(DB_NAME)
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        # Create students table if not exists
        if 'students' not in existing_tables:
            print("Creating students table...")
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
                filiere_id BIGINT UNSIGNED NOT NULL,
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
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (filiere_id) REFERENCES filieres(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
            print("Students table created successfully!")

        # Create rooms table if not exists
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

        # Create filieres table if not exists
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

        # Create room_history table if not exists
        if 'room_history' not in existing_tables:
            print("Creating room_history table...")
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

        conn.commit()
        print("All tables checked and created successfully!")
        
        # Run migrations
        migrate_database()
        
    except pymysql.Error as e:
        print(f"Error creating database/tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def reset_database():
    """Reset the entire database by dropping and recreating all tables."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS room_history")
        cursor.execute("DROP TABLE IF EXISTS students")
        cursor.execute("DROP TABLE IF EXISTS rooms")
        cursor.execute("DROP TABLE IF EXISTS filieres")
        
        # Recreate tables
        ensure_database_and_tables()
        return True
    except pymysql.Error as e:
        print(f"Error resetting database: {e}")
        return False
    finally:
        cursor.close()
        conn.close() 