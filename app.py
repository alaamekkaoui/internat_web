from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, send_file
from routes.student_route import student_bp
from routes.room_route import room_bp
from routes.filiere_route import filiere_bp
from routes.auth_route import auth_bp
from routes.user_route import user_bp
from routes.home_route import home_bp
from database.setup import ensure_database_and_tables, reset_database
from database.db import check_connection, get_connection
from models import create_dummy_data
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os 
from werkzeug.utils import secure_filename
from controllers.student_controller import StudentController
from controllers.room_controller import RoomController
from controllers.filiere_controller import FiliereController
from controllers.user_controller import UserController
from utilities.file_utils import handle_file_upload
from utilities.pdf_utils import generate_student_pdf
import tempfile

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

# Add context processor for datetime
@app.context_processor
def inject_now():
    return {'now': datetime.now(), 'current_academic_year': app.config.get('CURRENT_ACADEMIC_YEAR')}

@app.route('/')
def index():
    return render_template('home.html', current_academic_year=app.config.get('CURRENT_ACADEMIC_YEAR'))

# Debug and utility routes
@app.route('/debug', methods=['GET', 'POST'])
def debug_page():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'reset_db':
            try:
                reset_database()
                flash("Base de données réinitialisée avec succès!", "success")
            except Exception as e:
                flash(f"Erreur lors de la réinitialisation: {str(e)}", "danger")
                
        elif action == 'create_sample_data':
            try:
                create_dummy_data()
                flash("Données de test créées avec succès!", "success")
            except Exception as e:
                flash(f"Erreur lors de la création des données: {str(e)}", "danger")
                
        elif action == 'check_db':
            try:
                status = check_connection()
                if status:
                    flash("Connexion à la base de données réussie!", "success")
                else:
                    flash("Erreur de connexion à la base de données", "danger")
            except Exception as e:
                flash(f"Erreur lors de la vérification: {str(e)}", "danger")
                
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
    users = UserController().list_users()
    return render_template('user/list.html', users=users)

@app.route('/update_annee_universitaire', methods=['POST'])
def update_annee_universitaire():
    new_year = request.form.get('annee_universitaire')
    if not new_year:
        flash('Veuillez fournir une nouvelle année universitaire.', 'danger')
        return redirect(url_for('index'))
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE students SET annee_universitaire = %s", (new_year,))
        conn.commit()
        app.config['CURRENT_ACADEMIC_YEAR'] = new_year  # Update config
        flash(f"Année universitaire mise à jour pour tous les étudiants: {new_year}", 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Erreur lors de la mise à jour: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)