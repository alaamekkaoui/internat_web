from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from controllers.filiere_controller import FiliereController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required # Corrected path
from utilities.sample_filiere_utils import generate_sample_filieres_xlsx
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
@login_required
def import_filieres_xlsx():
    from utilities.xlsx_utils import import_xlsx
    file = request.files['file']
    data = import_xlsx(file)
    required_fields = ['name']
    cleaned_filieres = []
    for filiere in data:
        for field in required_fields:
            value = filiere.get(field, None)
            if value is None or value == '' or (isinstance(value, float) and (value != value)):
                filiere[field] = 'Non trouvé'
        cleaned_filieres.append(filiere)
    # Save or update filieres in DB
    from controllers.filiere_controller import FiliereController
    filiere_controller = FiliereController()
    imported_count = 0
    for filiere in cleaned_filieres:
        try:
            # Optionally, check for duplicates by name before adding
            filiere_controller.add_filiere(filiere)
            imported_count += 1
        except Exception as e:
            print(f"Erreur lors de l'import de la filière: {filiere.get('name', '')} - {e}")
            continue
    flash(f'{imported_count} filières importées avec succès!', 'success')
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

@filiere_bp.route('/filieres/sample-xlsx', methods=['GET'])
def download_sample_filieres_xlsx():
    return generate_sample_filieres_xlsx()

@filiere_bp.route('/filieres/bulk-action', methods=['POST'])
@login_required
def bulk_action_filieres():
    action = request.form.get('bulk_action')
    selected_ids = request.form.getlist('selected_filieres')
    if not selected_ids:
        flash('Aucune filière sélectionnée.', 'warning')
        return redirect(url_for('filiere.list_filieres'))
    # Get selected filieres
    filieres = [f for f in filiere_controller.list_filieres() if str(f['id']) in selected_ids]
    if action == 'delete':
        deleted = 0
        for fid in selected_ids:
            try:
                filiere_controller.delete_filiere(int(fid))
                deleted += 1
            except Exception as e:
                print(f"Erreur suppression filière {fid}: {e}")
        flash(f'{deleted} filière(s) supprimée(s) avec succès.', 'success')
        return redirect(url_for('filiere.list_filieres'))
    elif action == 'export_xlsx':
        import pandas as pd
        import io
        rows = []
        for f in filieres:
            rows.append({
                'ID': f.get('id', ''),
                'Nom': f.get('name', ''),
                'Date de création': f.get('created_at', '')
            })
        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='filieres_selection.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    elif action == 'export_pdf':
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        import io
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        content = []
        content.append(Paragraph("Liste des Filières (Sélection)", styles['Heading1']))
        content.append(Spacer(1, 20))
        table_data = [["ID", "Nom", "Date de création"]]
        for f in filieres:
            table_data.append([
                f.get('id', ''),
                f.get('name', ''),
                f.get('created_at', '')
            ])
        table = Table(table_data, colWidths=[1*inch, 2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(table)
        doc.build(content)
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name='filieres_selection.pdf',
            mimetype='application/pdf'
        )
    else:
        flash('Action non reconnue.', 'danger')
        return redirect(url_for('filiere.list_filieres'))
