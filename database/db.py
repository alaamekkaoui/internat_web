# database/db.py
import os
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor
import time

load_dotenv()

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB', 'internat')

def get_connection(use_db=True, max_retries=3, retry_delay=1):
    """Get a connection to the MySQL database with retry logic"""
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            if use_db:
                conn = pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DATABASE,
                    charset='utf8mb4',
                    cursorclass=DictCursor,
                    connect_timeout=10,
                    read_timeout=30,
                    write_timeout=30
                )
            else:
                conn = pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    charset='utf8mb4',
                    cursorclass=DictCursor,
                    connect_timeout=10,
                    read_timeout=30,
                    write_timeout=30
                )
            return conn
        except pymysql.Error as e:
            last_error = e
            retries += 1
            if retries < max_retries:
                print(f"Connection attempt {retries} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect after {max_retries} attempts. Last error: {e}")
                raise last_error

def execute_query(query, params=None, fetch=True, max_retries=3):
    """Execute a query with retry logic"""
    conn = None
    cursor = None
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
                
            return result
            
        except pymysql.Error as e:
            last_error = e
            retries += 1
            if retries < max_retries:
                print(f"Query attempt {retries} failed: {e}. Retrying...")
                time.sleep(1)  # Wait before retry
            else:
                print(f"Failed to execute query after {max_retries} attempts. Last error: {e}")
                raise last_error
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

def check_connection():
    """Check if database connection is working"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False
