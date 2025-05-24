# routes/room_route.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from controllers.room_controller import RoomController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required # Corrected path
from utilities.sample_room_utils import generate_sample_rooms_xlsx
import os

room_bp = Blueprint('room', __name__)
room_controller = RoomController()

@room_bp.route('/rooms', methods=['GET'])
def list_rooms():
    try:
        rooms = room_controller.list_rooms()
        return render_template('room/list.html', rooms=rooms)
    except Exception as e:
        flash(str(e), 'danger')
        return render_template('room/list.html', rooms=[])

@room_bp.route('/rooms/<int:room_id>', methods=['GET'])
def view_room(room_id):
    try:
        room = room_controller.get_room(room_id)
        if not room:
            flash('Chambre non trouvée', 'danger')
            return redirect(url_for('room.list_rooms'))
        
        # Get students in this room
        from models.student import Student
        students = Student().get_students_by_room(room['room_number'])
        
        return render_template('room/view.html', room=room, students=students)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    if request.method == 'POST':
        try:
            data = {
                'room_number': request.form.get('room_number'),
                'pavilion': request.form.get('pavilion'),
                'room_type': request.form.get('room_type'),
                'capacity': request.form.get('capacity')
            }
            # print(data) # Keep for debugging if necessary, but can be removed
            room_controller.add_room(data)
            flash('Chambre ajoutée avec succès!', 'success')
            return redirect(url_for('room.list_rooms'))
        except Exception as e:
            flash(str(e), 'danger')
            # It's good practice to return the form with entered data if possible
            return render_template('room/add.html', room_data=request.form) 
    return render_template('room/add.html')

@room_bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    try:
        room = room_controller.get_room(room_id)
        if not room:
            flash('Chambre non trouvée', 'danger')
            return redirect(url_for('room.list_rooms'))
        if request.method == 'POST':
            data = {
                'room_number': request.form.get('room_number'),
                'pavilion': request.form.get('pavilion'),
                'room_type': request.form.get('room_type'),
                'capacity': request.form.get('capacity'),
                'is_used': request.form.get('is_used', room.get('is_used', 0))
            }
            room_controller.update_room(room_id, data)
            flash('Chambre modifiée avec succès!', 'success')
            return redirect(url_for('room.view_room', room_id=room_id))
        return render_template('room/edit.html', room=room)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
# @role_required('admin') # Uncomment if only admins can delete
def delete_room(room_id):
    try:
        room_controller.delete_room(room_id)
        flash('Chambre supprimée avec succès!', 'success')
        return redirect(url_for('room.list_rooms'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/export/xlsx', methods=['GET'])
def export_rooms_xlsx():
    try:
        rooms = room_controller.list_rooms()
        # Prepare export with only relevant columns for rooms
        rows = []
        for room in rooms:
            rows.append({
                'Numéro': room.get('room_number', ''),
                'Pavillon': room.get('pavilion', ''),
                'Type': room.get('room_type', ''),
                'Capacité': room.get('capacity', ''),
                'Occupée': 'Oui' if room.get('is_used') else 'Non'
            })
        import pandas as pd
        import io
        from flask import send_file
        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='rooms.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/import/xlsx', methods=['POST'])
@login_required
def import_rooms_xlsx():
    from utilities.xlsx_utils import import_xlsx
    file = request.files['file']
    data = import_xlsx(file)
    required_fields = ['room_number', 'pavilion', 'room_type']
    cleaned_rooms = []
    for room in data:
        # Normalize and clean fields
        for field in required_fields:
            value = room.get(field, None)
            if value is None or value == '' or (isinstance(value, float) and (value != value)):
                room[field] = 'Non trouvé'
        # Normalize room_type
        room_type = str(room.get('room_type', '')).strip().lower()
        if room_type in ['simple', 'single', '1', '1 personne', '1 person', 's']:
            room['room_type'] = 'single'
        elif room_type in ['double', '2', '2 personnes', '2 person', 'd']:
            room['room_type'] = 'double'
        elif room_type in ['triple', '3', '3 personnes', '3 person', 't']:
            room['room_type'] = 'triple'
        else:
            room['room_type'] = 'single'  # Default to single if unrecognized
        # Set capacity based on room_type
        if room['room_type'] == 'single':
            room['capacity'] = 1
        elif room['room_type'] == 'double':
            room['capacity'] = 2
        elif room['room_type'] == 'triple':
            room['capacity'] = 3
        # Set is_used to False by default
        room['is_used'] = False
        cleaned_rooms.append(room)
    # Save or update rooms in DB
    from controllers.room_controller import RoomController
    room_controller = RoomController()
    imported_count = 0
    for room in cleaned_rooms:
        try:
            # Optionally, check for duplicates by room_number before adding
            room_controller.add_room(room)
            imported_count += 1
        except Exception as e:
            print(f"Erreur lors de l'import de la chambre: {room.get('room_number', '')} - {e}")
            continue
    flash(f'{imported_count} chambres importées avec succès!', 'success')
    return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/export/pdf', methods=['GET'])
def export_rooms_pdf():
    try:
        rooms = room_controller.list_rooms()
        # Prepare export with only relevant columns for rooms
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        import io
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        content = []
        content.append(Paragraph("Liste des Chambres", styles['Heading1']))
        content.append(Spacer(1, 20))
        table_data = [["Numéro", "Pavillon", "Type", "Capacité", "Occupée"]]
        for room in rooms:
            table_data.append([
                room.get('room_number', ''),
                room.get('pavilion', ''),
                room.get('room_type', ''),
                str(room.get('capacity', '')),
                'Oui' if room.get('is_used') else 'Non'
            ])
        table = Table(table_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
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
        from flask import send_file
        return send_file(
            buffer,
            as_attachment=True,
            download_name='rooms.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/sample-xlsx', methods=['GET'])
def download_sample_rooms_xlsx():
    return generate_sample_rooms_xlsx()

@room_bp.route('/rooms/bulk-action', methods=['POST'])
@login_required
def bulk_action_rooms():
    action = request.form.get('bulk_action')
    selected_ids = request.form.getlist('selected_rooms')
    if not selected_ids:
        flash('Aucune chambre sélectionnée.', 'warning')
        return redirect(url_for('room.list_rooms'))
    # Get selected rooms
    rooms = [room for room in room_controller.list_rooms() if str(room['id']) in selected_ids]
    if action == 'delete':
        deleted = 0
        for rid in selected_ids:
            try:
                room_controller.delete_room(int(rid))
                deleted += 1
            except Exception as e:
                print(f"Erreur suppression chambre {rid}: {e}")
        flash(f'{deleted} chambre(s) supprimée(s) avec succès.', 'success')
        return redirect(url_for('room.list_rooms'))
    elif action == 'export_xlsx':
        import pandas as pd
        import io
        from flask import send_file
        rows = []
        for room in rooms:
            rows.append({
                'Numéro': room.get('room_number', ''),
                'Pavillon': room.get('pavilion', ''),
                'Type': room.get('room_type', ''),
                'Capacité': room.get('capacity', ''),
                'Occupée': 'Oui' if room.get('is_used') else 'Non'
            })
        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='rooms_selection.xlsx',
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
        content.append(Paragraph("Liste des Chambres (Sélection)", styles['Heading1']))
        content.append(Spacer(1, 20))
        table_data = [["Numéro", "Pavillon", "Type", "Capacité", "Occupée"]]
        for room in rooms:
            table_data.append([
                room.get('room_number', ''),
                room.get('pavilion', ''),
                room.get('room_type', ''),
                str(room.get('capacity', '')),
                'Oui' if room.get('is_used') else 'Non'
            ])
        table = Table(table_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
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
        from flask import send_file
        return send_file(
            buffer,
            as_attachment=True,
            download_name='rooms_selection.pdf',
            mimetype='application/pdf'
        )
    else:
        flash('Action non reconnue.', 'danger')
        return redirect(url_for('room.list_rooms'))
