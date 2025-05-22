# controllers/student_controller.py
from models.student import Student

class StudentController:
    def __init__(self):
        self.student_model = Student()

    def list_students(self):
        return self.student_model.get_all_students()

    def add_student(self, data, files=None):
        print('[DEBUG] StudentController.add_student called')
        data_dict = dict(data)
        if files and 'photo' in files and files['photo'].filename:
            import os
            from utilities.file_utils import handle_file_upload
            filename = f"{data_dict.get('nom','')}_{data_dict.get('prenom','')}"
            result = handle_file_upload(
                file=files['photo'],
                filename_prefix=filename,
                upload_dir='static/uploads'
            )
            if result.get('success'):
                data_dict['photo'] = result['filename']
            else:
                print('[ERROR] StudentController.add_student: Photo upload failed')
                return {'error': result.get('error', 'Photo upload failed')}

        # Check room availability before adding
        from models.room import Room
        room_model = Room()
        if data_dict.get('num_chambre'):
            available_rooms = [r['room_number'] for r in room_model.get_available_rooms()]
            if data_dict['num_chambre'] not in available_rooms:
                from flask import flash
                flash('Selected room is not available.', 'danger')
                return {'error': 'Selected room is not available.'}

        # Add student
        result = self.student_model.add_student(data_dict)
        print(f'[DEBUG] StudentController.add_student result: {result}')
        
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
            return {'error': result['error']}
        if result is False or result is None:
            flash('Add failed (unknown error)', 'danger')
            return {'error': 'Add failed'}

        # Update room status immediately after adding student
        if data_dict.get('num_chambre'):
            room_model.set_room_used_status(data_dict['num_chambre'])
        
        return {'student_id': result}

    def get_student(self, student_id):
        return self.student_model.get_student_by_id(student_id)

    def update_student(self, student_id, data, files=None):
        print('[DEBUG] StudentController.update_student called')
        data_dict = dict(data)
        
        # Handle photo upload if present
        if files and 'photo' in files and files['photo'].filename:
            import os
            from utilities.file_utils import handle_file_upload
            filename = f"{data_dict.get('nom','')}_{data_dict.get('prenom','')}"
            result = handle_file_upload(
                file=files['photo'],
                filename_prefix=filename,
                upload_dir='static/uploads'
            )
            if result.get('success'):
                data_dict['photo'] = result['filename']
            else:
                print('[ERROR] StudentController.update_student: Photo upload failed')
                return {'error': result.get('error', 'Photo upload failed')}

        # Get current room before update
        current_student = self.student_model.get_student_by_id(student_id)
        current_room = current_student.get('num_chambre') if current_student else None
        new_room = data_dict.get('num_chambre')

        # Check room availability if changing rooms
        if new_room and new_room != current_room:
            from models.room import Room
            room_model = Room()
            available_rooms = [r['room_number'] for r in room_model.get_available_rooms()]
            if new_room not in available_rooms:
                from flask import flash
                flash('Selected room is not available.', 'danger')
                return {'error': 'Selected room is not available.'}

        # Update student
        result = self.student_model.update_student(student_id, data_dict)
        
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
            return {'error': result['error']}
        if result is False or result is None:
            flash('Update failed (unknown error)', 'danger')
            return {'error': 'Update failed'}

        # Update room statuses immediately after student update
        from models.room import Room
        room_model = Room()
        from flask import session
        
        # Update previous room if it exists and is different from new room
        if current_room and current_room != new_room:
            room_model.set_room_used_status(current_room)
            session['room_status_changed'] = True
            session['changed_room'] = current_room
        
        # Update new room if it exists
        if new_room:
            room_model.set_room_used_status(new_room)
            session['room_status_changed'] = True
            session['changed_room'] = new_room
        
        return {'success': True}

    def delete_student(self, student_id):
        # Get student's room before deletion
        student = self.student_model.get_student_by_id(student_id)
        room_number = student.get('num_chambre') if student else None
        
        # Delete student
        result = self.student_model.delete_student(student_id)
        
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
            return {'error': result['error']}
        if result is False:
            flash('Delete failed (unknown error)', 'danger')
            return {'error': 'Delete failed'}
        
        # Update room status immediately after deletion
        if room_number:
            from models.room import Room
            Room().set_room_used_status(room_number)
            from flask import session
            session['room_status_changed'] = True
            session['changed_room'] = room_number
        
        return {'status': 'success'}

    def update_student_image(self, student_id, filename):
        """Update only the student's photo."""
        try:
            result = self.student_model.update_student(student_id, {'photo': filename})
            if isinstance(result, dict) and 'error' in result:
                return {'error': result['error']}
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}

    def search_students(self, keyword=None, chambre=None):
        return self.student_model.search_students(keyword, chambre)
