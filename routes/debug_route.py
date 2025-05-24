# routes/debug_route.py
from flask import Blueprint, render_template, redirect, url_for, flash
from utils.debug_utils import (
    reset_database_util,
    create_sample_data_util,
    check_db_connection_util,
    cleanup_filieres_util,
    create_default_admin_user_util
)

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/reset-db', methods=['POST'])
def reset_db():
    reset_database_util()
    flash('Database reset and tables ensured.', 'success')
    return redirect(url_for('debug.debug_menu'))

@debug_bp.route('/debug/create-sample-data', methods=['POST'])
def create_sample_data():
    create_sample_data_util()
    flash('Sample data created.', 'success')
    return redirect(url_for('debug.debug_menu'))

@debug_bp.route('/debug/check-connection', methods=['POST'])
def check_connection():
    ok = check_db_connection_util()
    if ok:
        flash('Database connection successful.', 'success')
    else:
        flash('Database connection failed.', 'danger')
    return redirect(url_for('debug.debug_menu'))

@debug_bp.route('/debug/cleanup-filieres', methods=['POST'])
def cleanup_filieres():
    cleanup_filieres_util()
    flash('Filieres table cleaned up.', 'success')
    return redirect(url_for('debug.debug_menu'))

@debug_bp.route('/debug/create-admin', methods=['POST'])
def create_admin():
    create_default_admin_user_util()
    flash('Default admin user ensured.', 'success')
    return redirect(url_for('debug.debug_menu'))

@debug_bp.route('/debug', methods=['GET'])
def debug_menu():
    return render_template('debug.html')
