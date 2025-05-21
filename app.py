from flask import Flask , request, render_template, redirect, url_for, flash, jsonify
from routes.student_route import student_bp
from routes.room_route import room_bp
from routes.filiere_route import filiere_bp
from routes.auth_route import auth_bp # Ensure this is imported
from models import ensure_database_and_tables, reset_database, create_dummy_data, create_default_admin_user_if_not_exists # Ensure this is imported
from database.db import check_connection
from database.setup import migrate_database
from utils.decorators import role_required # Corrected path
import os 
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Check database connection
check_connection()

# Ensure DB and tables exist
ensure_database_and_tables()

# Run migrations
migrate_database()

# Create default admin user (should be from a previous task)
create_default_admin_user_if_not_exists()

# Register blueprints
app.register_blueprint(student_bp)
app.register_blueprint(room_bp)
app.register_blueprint(filiere_bp)
app.register_blueprint(auth_bp) # Ensure auth_bp is registered

# Add context processor for datetime
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    return render_template('home.html')

# Debug and utility routes can remain here
@app.route('/debug', methods=['GET', 'POST'])
@role_required('admin')
def debug_page():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'reset_db':
            reset_database()
            flash("Base de données réinitialisée !", "info")
        elif action == 'create_dummy':
            create_dummy_data()
            flash("Données fictives créées !", "success")
        return redirect(url_for('debug_page'))
    return render_template('debug.html')

@app.route('/debug/cleanup_filieres', methods=['POST'])
@role_required('admin')
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

# 

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)