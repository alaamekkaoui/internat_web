# routes/room_route.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from controllers.room_controller import RoomController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utilities.file_utils import handle_file_upload
from utilities.sample_utils import generate_sample_rooms_xlsx
from models.room import Room
from models.student import Student

room_bp = Blueprint('room', __name__)
room_controller = RoomController()

@room_bp.route('/rooms', methods=['GET'])
def list_rooms():
    print('room_route.list_rooms called')
    room_model = Room()
    rooms = room_model.get_all_rooms()
    return render_template('room/list.html', rooms=rooms)

@room_bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    print('room_route.add_room called')
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        result = room_controller.add_room(data)
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
            return render_template('room/add.html')
        flash('Room added successfully!', 'success')
        return redirect(url_for('room.list_rooms'))
    return render_template('room/add.html')

# --- ROUTE FIX: Avoid conflict between /rooms/add and /rooms/<room_number> ---
# Change all dynamic room routes to use /rooms/profile/<room_number>, /rooms/edit/<room_number>, etc.

@room_bp.route('/rooms/profile/<room_number>', methods=['GET'])
def view_room(room_number):
    room_model = Room()
    student_model = Student()
    
    # Get room details
    room_details = room_model.get_room_by_number(room_number)
    if not room_details:
        flash('Chambre non trouvée', 'error')
        return redirect(url_for('room.list_rooms'))
    
    # Get students assigned to this room
    assigned_students = student_model.get_students_by_room(room_number)
    
    return render_template('room/view.html', 
                         room=room_details, 
                         students=assigned_students)

@room_bp.route('/rooms/edit/<room_number>', methods=['GET', 'POST'])
@login_required
def edit_room(room_number):
    room_model = Room()
    room_data = room_model.get_room_by_number(room_number)
    if not room_data:
        flash('Chambre non trouvée', 'error')
        return redirect(url_for('room.list_rooms'))
    if request.method == 'POST':
        update_data = {
            'room_number': request.form.get('room_number'),
            'pavilion': request.form.get('pavilion'),
            'room_type': request.form.get('room_type'),
            'capacity': request.form.get('capacity')
        }
        if room_model.update_room(room_number, update_data):
            flash('Chambre mise à jour avec succès', 'success')
            return redirect(url_for('room.list_rooms'))
        else:
            flash('Erreur lors de la mise à jour de la chambre', 'error')
    return render_template('room/edit.html', room=room_data)

@room_bp.route('/rooms/delete/<room_number>', methods=['POST'])
@login_required
def delete_room(room_number):
    print('room_route.delete_room called')
    try:
        if room_controller.delete_room_by_number(room_number):
            flash('Chambre supprimée avec succès', 'success')
        else:
            flash('Erreur lors de la suppression de la chambre', 'error')
        return redirect(url_for('room.list_rooms'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/export/xlsx', methods=['GET'])
def export_rooms_xlsx():
    print('room_route.export_rooms_xlsx called')
    try:
        rooms = room_controller.list_rooms()
        return export_xlsx(rooms, filename='rooms.xlsx')
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/import/xlsx', methods=['POST'])
@login_required
def import_rooms_xlsx():
    print('room_route.import_rooms_xlsx called')
    file = request.files['file']
    data = import_xlsx(file)
    required_fields = ['room_number', 'pavilion', 'room_type']
    imported_count = 0
    from controllers.room_controller import RoomController
    room_controller = RoomController()
    imported_rooms = []
    failed_rooms = []
    existing_rooms = [r['room_number'] for r in room_controller.list_rooms()]
    for room in data:
        # Convert ImmutableMultiDict to dict if needed
        if hasattr(room, 'to_dict'):
            room = dict(room)
        else:
            room = dict(room)
        missing = [field for field in required_fields if not room.get(field) or str(room.get(field)).lower() == 'nan']
        warning = ''
        if missing:
            for field in missing:
                room[field] = None
            warning = f" (informations manquantes ou invalides: {', '.join(missing)}, valeur ignorée)"
        if room.get('room_number') in existing_rooms:
            failed_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b> - numéro déjà existant.")
            continue
        room['is_used'] = 0
        try:
            result = room_controller.add_room(room)
            if isinstance(result, dict) and result.get('error'):
                failed_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b> - erreur: {result['error']}{warning}")
            else:
                imported_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b>{warning}")
                imported_count += 1
        except Exception as e:
            failed_rooms.append(f"<b>Chambre {room.get('room_number', 'inconnu')}</b> - erreur technique: {e}{warning}")
    msg = f"<b>{imported_count} chambre(s) importée(s) avec succès !</b>"
    if imported_rooms:
        msg += '<br><u>Chambres ajoutées :</u><ul>' + ''.join(f'<li>{s}</li>' for s in imported_rooms) + '</ul>'
    if failed_rooms:
        msg += '<br><u>Chambres non ajoutées ou partiellement ajoutées :</u><ul>' + ''.join(f'<li>{s}</li>' for s in failed_rooms) + '</ul>'
    # --- AJAX/JSON support ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']:
        if failed_rooms:
            return jsonify({'success': False, 'error': msg})
        else:
            return jsonify({'success': True, 'message': msg})
    # --- End AJAX/JSON support ---
    if failed_rooms:
        flash(msg, 'warning')
    else:
        flash(msg, 'success')
    return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/export/pdf', methods=['GET'])
def export_rooms_pdf():
    print('room_route.export_rooms_pdf called')
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

@room_bp.route('/rooms/create', methods=['GET', 'POST'])
@login_required
def create_room():
    if request.method == 'POST':
        room_data = {
            'room_number': request.form.get('room_number'),
            'pavilion': request.form.get('pavilion'),
            'room_type': request.form.get('room_type'),
            'capacity': request.form.get('capacity')
        }
        
        room_model = Room()
        if room_model.create_room(room_data):
            flash('Chambre créée avec succès', 'success')
            return redirect(url_for('room.list_rooms'))
        else:
            flash('Erreur lors de la création de la chambre', 'error')
    
    return render_template('room/create.html')

@room_bp.route('/rooms/download-sample-xlsx', methods=['GET'])
def download_sample_rooms_xlsx():
    print('room_route.download_sample_rooms_xlsx called')
    return generate_sample_rooms_xlsx()
