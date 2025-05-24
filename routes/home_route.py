from flask import Blueprint, render_template, request, flash, redirect, url_for
from controllers.home_controller import HomeController
from utils.auth import login_required
from database.db import get_connection
from flask import current_app

home_bp = Blueprint('home', __name__)
home_controller = HomeController()

@home_bp.route('/')
@login_required
def home():
    print('home_route.home called')
    stats = home_controller.get_dashboard_stats()
    return render_template('home.html', **stats)

@home_bp.route('/update_annee_universitaire', methods=['POST'])
def update_annee_universitaire():
    print('home_route.update_annee_universitaire called')
    new_year = request.form.get('annee_universitaire')
    if not new_year:
        flash('Veuillez fournir une nouvelle année universitaire.', 'danger')
        return redirect(url_for('home.home'))
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE students SET annee_universitaire = %s", (new_year,))
        conn.commit()
        current_app.config['CURRENT_ACADEMIC_YEAR'] = new_year
        flash(f"Année universitaire mise à jour pour tous les étudiants: {new_year}", 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Erreur lors de la mise à jour: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('home.home'))