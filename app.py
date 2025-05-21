from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from routes.student_route import student_bp
from routes.room_route import room_bp
from routes.filiere_route import filiere_bp
from routes.auth_route import auth_bp
from routes.user_route import user_bp
from routes.home_route import home_bp
from database.setup import ensure_database_and_tables, reset_database
from database.db import check_connection
import os 
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

# Add context processor for datetime
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    return render_template('home.html')

# Debug and utility routes can remain here
@app.route('/debug', methods=['GET', 'POST'])
def debug_page():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'reset_db':
            reset_database()
            flash("Base de données réinitialisée !", "info")
        return redirect(url_for('debug_page'))
    return render_template('debug.html')

@app.route('/debug/cleanup_filieres', methods=['POST'])
def cleanup_filieres():
    from models.filiere import Filiere
    filiere_model = Filiere()
    try:
        filiere_model.cursor.execute("DELETE FROM filieres WHERE name = 'name' OR id = 'id' OR created_at = 'created_at'")
        filiere_model.conn.commit()
        flash('Header rows removed from filieres.', 'success')
    except Exception as e:
        filiere_model.conn.rollback()
        flash(f'Error cleaning up filieres: {e}', 'danger')
    return redirect(url_for('debug_page'))

@app.route('/debug/all')
def debug_all():
    return render_template('debug.html')

@app.route('/debug/student')
def debug_student():
    return render_template('student/list.html')

@app.route('/debug/room')
def debug_room():
    return render_template('room/list.html')

@app.route('/debug/filiere')
def debug_filiere():
    return render_template('filiere/list.html')

@app.route('/debug/user')
def debug_user():
    from controllers.user_controller import UserController
    users = UserController().list_users()
    return render_template('user/list.html', users=users)

# 

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)