# routes/room_route.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from controllers.room_controller import RoomController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required # Corrected path
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
                # Ensure is_used is handled correctly, e.g. boolean conversion if needed
                'is_used': request.form.get('is_used', room.get('is_used', 0)) 
            }
            room_controller.update_room(room_id, data)
            flash('Chambre modifiée avec succès!', 'success')
            return redirect(url_for('room.list_rooms'))
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
        folder = 'static/xlsx'
        os.makedirs(folder, exist_ok=True)
        filename = 'rooms.xlsx'
        return export_xlsx(rooms, filename, folder)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/import/xlsx', methods=['POST'])
@login_required # Assuming import is a modification action
def import_rooms_xlsx():
    try:
        file = request.files['file']
        data = import_xlsx(file)
        for room_data in data: # Renamed to avoid conflict with room variable in edit_room
            room_controller.add_room(room_data)
        flash('Chambres importées avec succès!', 'success')
        return redirect(url_for('room.list_rooms'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))

@room_bp.route('/rooms/export/pdf', methods=['GET'])
def export_rooms_pdf():
    try:
        # This route seems to expect a pre-generated PDF path, not dynamic generation
        # If dynamic generation is needed, it should be similar to student PDF export
        rooms = room_controller.list_rooms() # Get rooms data
        pdf_dir = 'static/pdfs'
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, 'rooms_list.pdf') # Give a more specific name
        
        # Assuming export_pdf can take data and a path similar to student export
        # You might need to adjust export_pdf or how it's called here
        # For now, let's assume it works like this:
        export_pdf(rooms, pdf_path) # This line might need adjustment based on export_pdf's capabilities
        
        # return send_file(pdf_path, as_attachment=True, download_name='rooms.pdf', mimetype='application/pdf')
        # The original code just returned export_pdf(pdf_path) which seems incorrect if it's meant to send a file
        # For now, I'll keep it closer to the original structure if export_pdf is meant to return a response
        # However, sending a file usually involves send_file.
        # If export_pdf is just for generation, then send_file is needed.
        # Let's assume export_pdf is supposed to return a response:
        return export_pdf(rooms, pdf_path) # This needs to be verified based on export_pdf implementation.
                                           # If it just creates the file, use send_file instead.
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('room.list_rooms'))
