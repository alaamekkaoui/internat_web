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
            file_ext = os.path.splitext(files['photo'].filename)[1].lower()
            if file_ext == '.jpeg':
                file_ext = '.jpg'
            elif file_ext not in ['.jpg', '.png', '.gif']:
                file_ext = '.jpg'
            filename = f"{data_dict.get('nom','')}_{data_dict.get('prenom','')}{file_ext}"
            result = handle_file_upload(
                file=files['photo'],
                filename_prefix=filename,
                upload_dir='static/uploads'
            )
            if result.get('success'):
                data_dict['photo'] = filename
            else:
                print('[ERROR] StudentController.add_student: Photo upload failed')
                return {'error': result.get('error', 'Photo upload failed')}
        # Only allow assignment to available rooms
        from models.room import Room
        available_rooms = [r['room_number'] for r in Room().get_available_rooms()]
        if data_dict.get('num_chambre') and data_dict['num_chambre'] not in available_rooms:
            from flask import flash
            flash('Selected room is not available.', 'danger')
            return {'error': 'Selected room is not available.'}
        result = self.student_model.add_student(data_dict)
        print(f'[DEBUG] StudentController.add_student result: {result}')
        from flask import flash
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
            return {'error': result['error']}
        if result is False or result is None:
            flash('Add failed (unknown error)', 'danger')
            return {'error': 'Add failed'}
        # After adding, recalculate room usage
        if data_dict.get('num_chambre'):
            Room().set_room_used_status(data_dict['num_chambre'])
        return {'student_id': result}

    def get_student(self, student_id):
        return self.student_model.get_student_by_id(student_id)

    def update_student(self, student_id, data, files=None):
        print('[DEBUG] StudentController.update_student called')
        data_dict = dict(data)
        if files and 'photo' in files and files['photo'].filename:
            import os
            from utilities.file_utils import handle_file_upload
            file_ext = os.path.splitext(files['photo'].filename)[1].lower()
            if file_ext == '.jpeg':
                file_ext = '.jpg'
            elif file_ext not in ['.jpg', '.png', '.gif']:
                file_ext = '.jpg'
            filename = f"{data_dict.get('nom','')}_{data_dict.get('prenom','')}{file_ext}"
            result = handle_file_upload(
                file=files['photo'],
                filename_prefix=filename,
                upload_dir='static/uploads'
            )
            if result.get('success'):
                data_dict['photo'] = filename
            else:
                print('[ERROR] StudentController.update_student: Photo upload failed')
                return {'error': result.get('error', 'Photo upload failed')}
        from models.room import Room
        available_rooms = [r['room_number'] for r in Room().get_available_rooms()]
        if data_dict.get('num_chambre') and data_dict['num_chambre'] not in available_rooms:
            from flask import flash
            flash('Selected room is not available.', 'danger')
            return {'error': 'Selected room is not available.'}
        result = self.student_model.update_student(student_id, data_dict)
        print(f'[DEBUG] StudentController.update_student result: {result}')
        from flask import flash
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
            return {'error': result['error']}
        if result is False:
            flash('Update failed (unknown error)', 'danger')
            return {'error': 'Update failed'}
        # After update, recalculate room usage
        if data_dict.get('num_chambre'):
            Room().set_room_used_status(data_dict['num_chambre'])
        return {'status': 'success'}

    def delete_student(self, student_id):
        from models.student import Student
        from models.room import Room
        student = Student().get_student_by_id(student_id)
        room_num = student['num_chambre'] if student and 'num_chambre' in student else None
        result = self.student_model.delete_student(student_id)
        from flask import flash
        if isinstance(result, dict) and 'error' in result:
            flash(result['error'], 'danger')
            return {'error': result['error']}
        if result is False:
            flash('Delete failed (unknown error)', 'danger')
            return {'error': 'Delete failed'}
        # After delete, recalculate room usage
        if room_num:
            Room().set_room_used_status(room_num)
        return {'status': 'success'}

    def update_student_image(self, student_id, filename):
        return self.student_model.update_student_image(student_id, filename)

    def search_students(self, keyword=None, chambre=None):
        return self.student_model.search_students(keyword, chambre)
