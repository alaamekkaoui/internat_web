from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from controllers.filiere_controller import FiliereController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utilities.file_utils import handle_file_upload
from utilities.sample_utils import generate_sample_filieres_xlsx

filiere_bp = Blueprint('filiere', __name__)
filiere_controller = FiliereController()

@filiere_bp.route('/filieres', methods=['GET'])
def list_filieres():
    print('filiere_route.list_filieres called')
    filieres = filiere_controller.list_filieres()
    return render_template('filiere/list.html', filieres=filieres)

@filiere_bp.route('/filieres/add', methods=['POST'])
@login_required
def add_filiere():
    print('filiere_route.add_filiere called')
    try:
        data = request.form.to_dict()
        result = filiere_controller.add_filiere(data)
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
        else:
            flash('Filière ajoutée avec succès!', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/<int:filiere_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_filiere(filiere_id):
    print('filiere_route.edit_filiere called')
    filiere = filiere_controller.get_filiere(filiere_id)
    if not filiere:
        flash('Filière non trouvée', 'danger')
        return redirect(url_for('filiere.list_filieres'))
    if request.method == 'POST':
        data = request.form.to_dict()
        data['id'] = filiere_id
        result = filiere_controller.update_filiere(filiere_id, data)
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
        else:
            flash('Filière mise à jour avec succès!', 'success')
        return redirect(url_for('filiere.list_filieres'))
    return render_template('filiere/edit.html', filiere=filiere)

@filiere_bp.route('/filieres/<int:filiere_id>/delete', methods=['POST'])
@login_required
def delete_filiere(filiere_id):
    print('filiere_route.delete_filiere called')
    try:
        result = filiere_controller.delete_filiere(filiere_id)
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
        else:
            flash('Filière supprimée avec succès!', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/export/xlsx', methods=['GET'])
def export_filieres_xlsx():
    print('filiere_route.export_filieres_xlsx called')
    try:
        filieres = filiere_controller.list_filieres()
        return export_xlsx(filieres, filename='filieres.xlsx')
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/import/xlsx', methods=['POST'])
@login_required
def import_filieres_xlsx():
    print('filiere_route.import_filieres_xlsx called')
    file = request.files['file']
    data = import_xlsx(file)
    required_fields = ['name']
    imported_count = 0
    imported_filieres = []
    failed_filieres = []
    existing_filieres = [f['name'] for f in filiere_controller.list_filieres()]
    for filiere in data:
        # Convert ImmutableMultiDict to dict if needed
        if hasattr(filiere, 'to_dict'):
            filiere = dict(filiere)
        else:
            filiere = dict(filiere)
        missing = [field for field in required_fields if not filiere.get(field) or str(filiere.get(field)).lower() == 'nan']
        warning = ''
        if missing:
            for field in missing:
                filiere[field] = None
            warning = f" (informations manquantes ou invalides: {', '.join(missing)}, valeur ignorée)"
        if filiere.get('name') in existing_filieres:
            failed_filieres.append(f"<b>Filière {filiere.get('name', 'inconnu')}</b> - nom déjà existant.")
            continue
        try:
            result = filiere_controller.add_filiere(filiere)
            if isinstance(result, dict) and result.get('error'):
                failed_filieres.append(f"<b>Filière {filiere.get('name', 'inconnu')}</b> - erreur: {result['error']}{warning}")
            else:
                imported_filieres.append(f"<b>Filière {filiere.get('name', 'inconnu')}</b>{warning}")
                imported_count += 1
        except Exception as e:
            failed_filieres.append(f"<b>Filière {filiere.get('name', 'inconnu')}</b> - erreur technique: {e}{warning}")
    msg = f"<b>{imported_count} filière(s) importée(s) avec succès !</b>"
    if imported_filieres:
        msg += '<br><u>Filières ajoutées :</u><ul>' + ''.join(f'<li>{s}</li>' for s in imported_filieres) + '</ul>'
    if failed_filieres:
        msg += '<br><u>Filières non ajoutées ou partiellement ajoutées :</u><ul>' + ''.join(f'<li>{s}</li>' for s in failed_filieres) + '</ul>'
    # --- AJAX/JSON support ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']:
        if failed_filieres:
            return jsonify({'success': False, 'error': msg})
        else:
            return jsonify({'success': True, 'message': msg})
    # --- End AJAX/JSON support ---
    if failed_filieres:
        flash(msg, 'warning')
    else:
        flash(msg, 'success')
    return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/export/pdf', methods=['GET'])
def export_filieres_pdf():
    print('filiere_route.export_filieres_pdf called')
    try:
        filieres = filiere_controller.list_filieres()
        if isinstance(filieres, dict) and 'error' in filieres:
            flash(filieres['error'], 'danger')
            return redirect(url_for('filiere.list_filieres'))

        # Generate PDF
        pdf_buffer = export_pdf(filieres)
        if not pdf_buffer:
            flash('Erreur lors de la génération du PDF', 'danger')
            return redirect(url_for('filiere.list_filieres'))

        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_buffer.getvalue())
            tmp_path = tmp.name

        # Send the file and then delete it
        try:
            return send_file(
                tmp_path,
                as_attachment=True,
                download_name='filieres.pdf',
                mimetype='application/pdf'
            )
        finally:
            # Clean up the temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('filiere.list_filieres'))

@filiere_bp.route('/filieres/download-sample-xlsx', methods=['GET'])
def download_sample_filieres_xlsx():
    print('filiere_route.download_sample_filieres_xlsx called')
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
