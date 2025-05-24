# utils/debug_utils.py
# Centralized debug and utility functions for the app

def reset_database_util():
    from database.db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Drop all main tables if they exist
        cursor.execute("DROP TABLE IF EXISTS room_history")
        cursor.execute("DROP TABLE IF EXISTS students")
        cursor.execute("DROP TABLE IF EXISTS rooms")
        cursor.execute("DROP TABLE IF EXISTS filieres")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error dropping tables: {e}")
    finally:
        cursor.close()
        conn.close()
    # Recreate tables
    from models import ensure_database_and_tables
    ensure_database_and_tables()

def create_sample_data_util():
    from models import create_dummy_data
    create_dummy_data()

def check_db_connection_util():
    from database.db import check_connection
    return check_connection()

def cleanup_filieres_util():
    from models.filiere import Filiere
    filiere_model = Filiere()
    filiere_model.cursor.execute("DELETE FROM filieres WHERE name = 'name' OR id = 'id' OR created_at = 'created_at'")
    filiere_model.conn.commit()

def create_default_admin_user_util():
    """Create a default admin user if no users exist"""
    try:
        from models.user import User
        user_model = User()
        
        # Check if admin user already exists
        admin_user = user_model.get_user_by_username('admin')
        if admin_user:
            print("Admin user already exists")
            return True
        
        # Create admin user
        success, message = user_model.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        
        if success:
            print("Default admin user created successfully")
            return True
        else:
            print(f"Error creating admin user: {message}")
            return False
            
    except Exception as e:
        print(f"Error in create_default_admin_user_util: {str(e)}")
        return False
