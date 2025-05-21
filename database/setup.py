import sqlite3
import os
from models.user import User

def get_connection():
    """Get a connection to the SQLite database"""
    db_path = 'internat.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
    """Reset the entire database by dropping and recreating all tables."""
    try:
        # Delete the database file if it exists
        if os.path.exists('internat.db'):
            os.remove('internat.db')
            print("Old database file removed.")
        
        # Create new database and tables
        ensure_database_and_tables()
        print("Database reset successfully!")
        return True
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False

def ensure_database_and_tables():
    """Ensure database and tables exist"""
    try:
        # Create tables
        create_tables()
        
        # Create default admin user if no users exist
        user_model = User()
        user_model.create_default_admin()
        
        print("Database and tables initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    ensure_database_and_tables() 