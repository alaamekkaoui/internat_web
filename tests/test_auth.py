# tests/test_auth.py
import unittest
import os
from app import app # Your Flask app instance
from models import reset_database, ensure_database_and_tables, create_default_admin_user_if_not_exists
from models.user import User
from database.db import get_connection

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms if you use Flask-WTF
        app.config['SECRET_KEY'] = 'test_secret_key' # Use a fixed secret key for session testing
        
        # Use a separate test database if possible, or reset current one
        # For this example, we'll ensure the DB is clean and has the schema
        # It's CRITICAL that MYSQL_DATABASE is set in the environment for testing
        # or that db.py and models/__init__.py can handle a test config.
        # Assuming environment variables are set for a test database or dev database.
        print("Setting up test database...")
        reset_database() # Clears data and recreates tables
        create_default_admin_user_if_not_exists() # Ensure admin exists

        self.client = app.test_client()

        # Optional: Check if admin was created
        admin = User.find_by_username('admin')
        if admin:
            print(f"Admin user '{admin.username}' found with role '{admin.role}'.")
        else:
            print("Admin user not found during setUp.")


    def tearDown(self):
        # Clean up after tests if necessary
        # For instance, reset the database again
        # reset_database()
        # For now, we'll leave the DB as is after tests, or you can clean it.
        # Close any open connections if your models don't handle it well in test env.
        pass

    def register(self, username, password, confirm_password):
        return self.client.post('/auth/register', data=dict(
            username=username,
            password=password,
            confirm_password=confirm_password
        ), follow_redirects=True)

    def login(self, username, password):
        return self.client.post('/auth/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    # Test Cases
    def test_01_registration(self):
        print("\nRunning test_01_registration...")
        # Test successful registration
        response = self.register('testuser', 'password123', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful! Please login.', response.data)
        
        # Verify user in database
        user = User.find_by_username('testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'user') # Should default to 'user'

        # Test registration with existing username
        response = self.register('testuser', 'password123', 'password123')
        self.assertEqual(response.status_code, 200) # Assuming redirect leads to 200
        self.assertIn(b'Username already exists.', response.data)

        # Test registration with mismatched passwords
        response = self.register('newuser', 'pass1', 'pass2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match.', response.data)
        print("test_01_registration completed.")

    def test_02_login_logout(self):
        print("\nRunning test_02_login_logout...")
        # Register a user first (or use admin)
        self.register('loginuser', 'loginpass', 'loginpass')

        # Test successful login
        response = self.login('loginuser', 'loginpass')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data)
        self.assertIn(b'Welcome, loginuser', response.data) # Check for welcome message

        # Test logout
        logout_response = self.logout()
        self.assertEqual(logout_response.status_code, 200)
        self.assertIn(b'You have been logged out.', logout_response.data)
        self.assertNotIn(b'Welcome, loginuser', logout_response.data)

        # Test login with invalid credentials
        response = self.login('loginuser', 'wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password.', response.data)
        print("test_02_login_logout completed.")

    def test_03_default_admin_login(self):
        print("\nRunning test_03_default_admin_login...")
        # Test admin login
        admin = User.find_by_username('admin') # Verify admin exists from setup
        self.assertIsNotNone(admin, "Admin user should exist for this test.")
        self.assertEqual(admin.role, 'admin')

        response = self.login('admin', 'adminpassword') # Use the default admin password
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data)
        self.assertIn(b'Welcome, admin (admin)', response.data)
        self.logout() # Logout admin for subsequent tests
        print("test_03_default_admin_login completed.")

    def test_04_access_control_debug_routes_admin_only(self):
        print("\nRunning test_04_access_control_debug_routes_admin_only...")
        # Test access to /debug by non-admin (should fail/redirect)
        self.register('normaluser', 'userpass', 'userpass')
        self.login('normaluser', 'userpass')
        
        response = self.client.get('/debug', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You do not have permission to access this page.', response.data)
        # Should be redirected to index page or show flashed message on current page
        # Check if it redirects to home ('/')
        self.assertTrue(response.request.path == '/', "Non-admin should be redirected from /debug")

        self.logout()

        # Test access to /debug by admin (should succeed)
        self.login('admin', 'adminpassword')
        response = self.client.get('/debug', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'You do not have permission', response.data)
        self.assertIn(b'Debug Information', response.data) # Assuming 'Debug Information' is on debug.html
        self.logout()
        print("test_04_access_control_debug_routes_admin_only completed.")

    def test_05_access_control_data_modification_routes_login_required(self):
        print("\nRunning test_05_access_control_data_modification_routes_login_required...")
        # Test access to a login-required page (e.g., /students/add) when not logged in
        response = self.client.get('/students/add', follow_redirects=True) # Corrected path
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access this page.', response.data)
        # Check if it redirects to login page
        self.assertTrue(response.request.path == '/auth/login', "Should redirect to /auth/login")


        # Register and login as a normal user
        self.register('datauser', 'datapass', 'datapass')
        self.login('datauser', 'datapass')

        # Test access to /students/add when logged in (Corrected path)
        response = self.client.get('/students/add', follow_redirects=True) # Corrected path
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Please log in', response.data)
        # This assertion might fail if the actual title is different.
        # Example: Check for a unique element or text on the 'student/add.html' page.
        self.assertIn(b'Ajouter un étudiant', response.data) # Assuming 'Ajouter un étudiant' is on student add page
        
        self.logout()
        print("test_05_access_control_data_modification_routes_login_required completed.")

if __name__ == '__main__':
    # Ensure environment variables are set, especially MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST
    # e.g., os.environ['MYSQL_DATABASE'] = 'test_your_app_db'
    # It's better to configure this outside the script or via a test runner config.
    
    # Check for MYSQL_DATABASE env var
    if not os.environ.get('MYSQL_DATABASE'):
        print("Error: MYSQL_DATABASE environment variable not set.")
        print("Please set it before running tests, e.g., export MYSQL_DATABASE=your_test_db_name")
        # exit(1) # Or set a default test DB name, but this is risky
        # For the purpose of this tool, we'll try to proceed, but it might fail if DB is not configured.
        os.environ['MYSQL_DATABASE'] = 'flask_db_test_auth' # Fallback for tool, real env should set this
        os.environ['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root') # Default to root if not set
        os.environ['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '') # Default to empty if not set
        os.environ['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost') # Default to localhost if not set
        print(f"Falling back to MYSQL_DATABASE={os.environ['MYSQL_DATABASE']}")


    unittest.main()
