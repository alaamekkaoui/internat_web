# database/db.py
import os
from dotenv import load_dotenv
import pymysql
from .config import DB_CONFIG

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def check_connection():
    """Check if database connection is working and print connection details."""
    try:
        print("\n=== Attempting Database Connection ===")
        print(f"Connecting to {DB_CONFIG['host']} as {DB_CONFIG['user']}...")
        
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        
        print("✓ Successfully connected to MySQL server")
        
        # Try to select the database
        try:
            print(f"Attempting to select database '{DB_CONFIG['database']}'...")
            conn.select_db(DB_CONFIG['database'])
            print("✓ Successfully selected database")
            
            # Check if we can execute a query
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Found {len(tables)} tables in database")
            cursor.close()
            
        except pymysql.Error as e:
            print(f"✗ Error selecting database: {e}")
            print("Attempting to create database...")
            try:
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` DEFAULT CHARACTER SET 'utf8mb4'")
                conn.commit()
                cursor.close()
                print("✓ Database created successfully")
                conn.select_db(DB_CONFIG['database'])
                print("✓ Successfully selected database")
            except pymysql.Error as e:
                print(f"✗ Error creating database: {e}")
            
        conn.close()
        print("===============================\n")
        
    except pymysql.Error as e:
        print("\n=== Database Connection Error ===")
        print(f"✗ Failed to connect to MySQL: {e}")
        print("\nPlease check:")
        print("1. MySQL server is running")
        print("2. MySQL credentials are correct")
        print("3. MySQL user has proper permissions")
        print("===============================\n")

def get_connection(use_db=True):
    """Get a database connection.
    
    Args:
        use_db (bool): Whether to include the database name in the connection.
                      Set to False when creating the database.
    """
    config = DB_CONFIG.copy()
    if not use_db:
        config.pop('database', None)
    
    try:
        conn = pymysql.connect(**config)
        return conn
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        raise
