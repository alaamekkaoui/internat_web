# routes/room_route.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from controllers.room_controller import RoomController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required # Corrected path
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utilities.file_utils import handle_file_upload
from utilities.sample_utils import generate_sample_rooms_xlsx

room_bp = Blueprint('room', __name__)
room_controller = RoomController()

@room_bp.route('/rooms', methods=['GET'])
def list_rooms():
    rooms = room_controller.list_rooms()
    return render_template('room/list.html', rooms=rooms)

@room_bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    if request.method == 'POST':
        data = request.form
        result = room_controller.add_room(data)
        if 'error' in result:
            flash(result['error'], 'danger')
            return render_template('room/add.html')
        flash('Room added successfully!', 'success')
        return redirect(url_for('room.list_rooms'))
    return render_template('room/add.html')

@room_bp.route('/rooms/<int:room_id>', methods=['GET'])
def room_profile(room_id):
    result = room_controller.get_room(room_id)
    if 'error' in result:
        flash(result['error'], 'danger')
        return redirect(url_for('room.list_rooms'))
    return render_template('room/profile.html', room=result)

@room_bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
# @role_required('admin') # Uncomment if only admins can delete
def delete_room(room_id):
    try:
        result = room_controller.delete_room(room_id)
        if 'error' in result:
            flash(result['error'], 'danger')
            return redirect(url_for('room.list_rooms'))
        flash('Room deleted successfully!', 'success')
        return redirect(url_for('room.list_rooms'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/export/xlsx', methods=['GET'])
def export_rooms_xlsx():
    try:
        rooms = room_controller.list_rooms()
        return export_xlsx(rooms, filename='rooms.xlsx')
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/import/xlsx', methods=['POST'])
@login_required
def import_rooms_xlsx():
    from utilities.xlsx_utils import import_xlsx
    file = request.files['file']
    data = import_xlsx(file)
    required_fields = ['room_number', 'capacity', 'pavilion']  # filiere is optional
    errors = []
    imported_count = 0
    from controllers.room_controller import RoomController
    room_controller = RoomController()
    imported_rooms = []
    failed_rooms = []
    for room in data:
        # Check required fields
        missing = [field for field in required_fields if not room.get(field)]
        if missing:
            failed_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b> - informations manquantes: {', '.join(missing)}")
            continue
        try:
            result = room_controller.add_room(room)
            if isinstance(result, dict) and result.get('error'):
                failed_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b> - erreur: {result['error']}")
            else:
                imported_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b>")
                imported_count += 1
        except Exception as e:
            failed_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b> - erreur technique: {e}")
    msg = f"<b>{imported_count} chambre(s) importée(s) avec succès !</b>"
    if imported_rooms:
        msg += '<br><u>Chambres ajoutées :</u><ul>' + ''.join(f'<li>{s}</li>' for s in imported_rooms) + '</ul>'
    if failed_rooms:
        msg += '<br><u>Chambres non ajoutées ou partiellement ajoutées :</u><ul>' + ''.join(f'<li>{s}</li>' for s in failed_rooms) + '</ul>'
        flash(msg, 'warning')
    else:
        flash(msg, 'success')
    return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/export/pdf', methods=['GET'])
def export_rooms_pdf():
    try:
        rooms = room_controller.list_rooms()
        if isinstance(rooms, dict) and 'error' in rooms:
            flash(rooms['error'], 'danger')
            return redirect(url_for('room.list_rooms'))
        from utilities.pdf_utils import export_pdf
        pdf_buffer = export_pdf(rooms)
        if not pdf_buffer:
            flash('Error generating PDF', 'danger')
            return redirect(url_for('room.list_rooms'))
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name='rooms.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/<int:room_id>/modify', methods=['GET', 'POST'])
@login_required
def modify_room(room_id):
    if request.method == 'POST':
        data = request.form
        result = room_controller.update_room(room_id, data)
        if 'error' in result:
            flash(result['error'], 'danger')
            room = room_controller.get_room(room_id)
            return render_template('room/edit.html', room=room)
        flash('Room updated successfully!', 'success')
        return redirect(url_for('room.room_profile', room_id=room_id))
    # GET request - show edit form
    room = room_controller.get_room(room_id)
    if 'error' in room:
        flash(room['error'], 'danger')
        return redirect(url_for('room.list_rooms'))
    # Ensure room is an object with attribute access for Jinja
    class RoomObj(dict):
        def __getattr__(self, item):
            return self.get(item)
    room_obj = RoomObj(room)
    return render_template('room/edit.html', room=room_obj)

@room_bp.route('/rooms/download-sample-xlsx', methods=['GET'])
def download_sample_rooms_xlsx():
    return generate_sample_rooms_xlsx()
