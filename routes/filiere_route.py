from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from controllers.filiere_controller import FiliereController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required # Corrected path
import os

filiere_bp = Blueprint('filiere', __name__)
filiere_controller = FiliereController()

@filiere_bp.route('/filieres', methods=['GET'])
def list_filieres():
    try:
        filieres = filiere_controller.list_filieres()
        # print(filieres) # Keep for debugging if necessary
        return render_template('filiere/list.html', filieres=filieres)
    except Exception as e:
        flash(str(e), 'danger')
        return render_template('filiere/list.html', filieres=[])

@filiere_bp.route('/filieres/add', methods=['GET', 'POST'])
@login_required
def add_filiere():
    if request.method == 'POST':
        try:
            data = {
                'name': request.form.get('name')
            }
            # print(data) # Keep for debugging if necessary
            filiere_controller.add_filiere(data)
            flash('Filière ajoutée avec succès!', 'success')
            return redirect(url_for('filiere.list_filieres'))
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('filiere/add.html', filiere_data=request.form)
    return render_template('filiere/add.html')

@filiere_bp.route('/filieres/<int:filiere_id>', methods=['GET'])
def get_filiere(filiere_id): # Assuming viewing a single filiere is public
    try:
        filiere = filiere_controller.get_filiere(filiere_id)
        # print(filiere) # Keep for debugging if necessary
        if not filiere:
            flash('Filière non trouvée', 'danger')
            return redirect(url_for('filiere.list_filieres'))
        return render_template('filiere/view.html', filiere=filiere)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/<int:filiere_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_filiere(filiere_id):
    try:
        filiere = filiere_controller.get_filiere(filiere_id)
        if not filiere:
            flash('Filière non trouvée', 'danger')
            return redirect(url_for('filiere.list_filieres'))

        if request.method == 'POST':
            data = {
                'name': request.form.get('name')
            }
            filiere_controller.update_filiere(filiere_id, data)
            flash('Filière modifiée avec succès!', 'success')
            return redirect(url_for('filiere.list_filieres'))
        return render_template('filiere/edit.html', filiere=filiere)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/<int:filiere_id>/delete', methods=['POST']) # Changed to POST for consistency
@login_required
# @role_required('admin') # Uncomment if only admins can delete
def delete_filiere_post(filiere_id): # Renamed to avoid conflict if you have a GET delete
    try:
        filiere_controller.delete_filiere(filiere_id)
        flash('Filière supprimée avec succès!', 'success') # Flash message for POST
    except Exception as e:
        flash(f'Erreur lors de la suppression: {str(e)}', 'danger')
    return redirect(url_for('filiere.list_filieres'))

# If you still need a DELETE method via JS that returns JSON:
@filiere_bp.route('/filieres/<int:filiere_id>/api_delete', methods=['DELETE'])
@login_required
# @role_required('admin')
def delete_filiere_api(filiere_id):
    try:
        filiere_controller.delete_filiere(filiere_id)
        return jsonify({'status': 'success', 'message': 'Filière supprimée avec succès!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@filiere_bp.route('/filieres/export/xlsx', methods=['GET'])
def export_filieres_xlsx():
    try:
        filieres = filiere_controller.list_filieres()
        folder = 'static/xlsx'
        os.makedirs(folder, exist_ok=True)
        filename = 'filieres.xlsx'
        return export_xlsx(filieres, filename, folder)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/import/xlsx', methods=['POST'])
@login_required # Assuming import is a modification action
def import_filieres_xlsx():
    try:
        file = request.files['file']
        data = import_xlsx(file)
        for filiere_data in data: # Renamed to avoid conflict
            # Skip header or invalid rows
            if filiere_data.get('name', '').lower() != 'name' and filiere_data.get('id', '').lower() != 'id':
                filiere_controller.add_filiere(filiere_data)
        flash('Filières importées avec succès!', 'success')
        return redirect(url_for('filiere.list_filieres'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/export/pdf', methods=['GET'])
def export_filieres_pdf():
    try:
        # Similar to room_route, this needs to be clarified how export_pdf works
        filieres = filiere_controller.list_filieres()
        pdf_dir = 'static/pdfs'
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, 'filieres_list.pdf')
        
        # Assuming export_pdf can take data and a path:
        export_pdf(filieres, pdf_path) # This might need adjustment
        
        # If export_pdf generates the file and returns path or True:
        # return send_file(pdf_path, as_attachment=True, download_name='filieres.pdf', mimetype='application/pdf')
        # Keeping closer to original if export_pdf is meant to return a response:
        return export_pdf(filieres, pdf_path) # Verify this
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('filiere.list_filieres'))
