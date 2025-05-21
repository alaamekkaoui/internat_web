# database/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
env_path = os.path.join(ROOT_DIR, '.env')
load_dotenv(dotenv_path=env_path)

# Required environment variables
REQUIRED_ENV_VARS = [
    'MYSQL_HOST',
    'MYSQL_USER',
    'MYSQL_PASSWORD',
    'MYSQL_DATABASE'
]

# Check if all required environment variables are set
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    print("\n=== Missing Environment Variables ===")
    print("The following required environment variables are not set:")
    for var in missing_vars:
        print(f"- {var}")
    print("\nPlease set these variables in your .env file")
    print("===============================\n")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4'
}

# Print configuration for debugging
print("\n=== Database Configuration ===")
print(f"Host: {DB_CONFIG['host']}")
print(f"User: {DB_CONFIG['user']}")
print(f"Database: {DB_CONFIG['database']}")
print("=============================\n")

