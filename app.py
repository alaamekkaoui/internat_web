from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, send_file
from routes.student_route import student_bp
from routes.room_route import room_bp
from routes.filiere_route import filiere_bp
from routes.auth_route import auth_bp
from routes.user_route import user_bp
from routes.home_route import home_bp
from routes.debug_route import debug_bp
from database.db import check_connection, get_connection
from models import  ensure_database_and_tables
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os 
import tempfile
from utils.decorators import generate_csrf_token

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


# Set academic year based on current year
current_year = datetime.now().year
next_year = current_year + 1
app.config['CURRENT_ACADEMIC_YEAR'] = f"{current_year}/{next_year}"

# Check database connection
check_connection()

# Ensure DB and tables exist
ensure_database_and_tables()

# Register blueprints
app.register_blueprint(student_bp)
app.register_blueprint(room_bp)
app.register_blueprint(filiere_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp)
app.register_blueprint(home_bp)
app.register_blueprint(debug_bp)

# Initialize database
get_connection()

# Add context processor for datetime
@app.context_processor
def inject_now():
    return {'now': datetime.now(), 'current_academic_year': app.config.get('CURRENT_ACADEMIC_YEAR')}

def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token)

app.context_processor(inject_csrf_token)

@app.route('/')
def index():
    return render_template('home.html', current_academic_year=app.config.get('CURRENT_ACADEMIC_YEAR'))

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)