# controllers/student_controller.py
from models.student import Student

class StudentController:
    def __init__(self):
        self.student_model = Student()

    def list_students(self):
        return self.student_model.get_all_students()

    def get_paginated_students(self, page=1, per_page=10, search='', filiere_id=None, internat='', pavilion=None, chambre=None):
        """
        Get paginated students with optional filtering
        Returns a tuple of (students, total_count)
        """
        # Get all students first (we'll filter them in memory)
        all_students = self.list_students()
        filtered_students = all_students

        if search:
            search = search.lower()
            filtered_students = [
                s for s in filtered_students
                if search in s.get('nom', '').lower() or
                   search in s.get('prenom', '').lower() or
                   search in s.get('matricule', '').lower() or
                   search in s.get('cin', '').lower()
            ]
        if filiere_id:
            filtered_students = [
                s for s in filtered_students
                if s.get('filiere_id') == filiere_id
            ]
        if internat:
            if internat == 'aucun':
                filtered_students = [
                    s for s in filtered_students
                    if not s.get('type_section')
                ]
            else:
                filtered_students = [
                    s for s in filtered_students
                    if s.get('type_section') == internat
                ]
        if pavilion:
            filtered_students = [
                s for s in filtered_students
                if s.get('pavilion') == pavilion
            ]
        if chambre:
            filtered_students = [
                s for s in filtered_students
                if s.get('num_chambre') == chambre
            ]
        # Calculate pagination
        total = len(filtered_students)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_students = filtered_students[start_idx:end_idx]
        return paginated_students, total

    def add_student(self, data, files=None):
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
        result = self.student_model.add_student(data_dict)
        if result is False or result is None:
            return {'error': 'Add failed'}
        return {'student_id': result}

    def get_student(self, student_id):
        return self.student_model.get_student_by_id(student_id)

    def update_student(self, student_id, data, files=None):
        data_dict = dict(data)
        
        # Get existing student data to preserve values
        existing_student = self.get_student(student_id)
        if not existing_student:
            return {'error': 'Student not found'}
            
        # Preserve existing values for empty fields
        for key in data_dict:
            if data_dict[key] in [None, '', 'None', 'none', 'null']:
                data_dict[key] = existing_student.get(key)
        
        # Handle photo separately
        if existing_student:
            data_dict['photo'] = existing_student.get('photo')  # Preserve existing photo by default
            
        if files and 'photo' in files and files['photo'].filename:
            import os
            from utilities.file_utils import handle_file_upload, delete_file
            
            # Delete old photo if it exists
            if existing_student and existing_student.get('photo'):
                old_photo_path = os.path.join('static', 'uploads', existing_student['photo'])
                delete_file(old_photo_path)
            
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
                
        result = self.student_model.update_student(student_id, data_dict)
        if result is False:
            return {'error': 'Update failed'}
        return {'status': 'success'}

    def delete_student(self, student_id):
        return self.student_model.delete_student(student_id)

    def update_student_image(self, student_id, filename):
        return self.student_model.update_student_image(student_id, filename)

    def search_students(self, keyword=None, chambre=None):
        return self.student_model.search_students(keyword, chambre)

    def get_filtered_students(self, type_section='', keyword='', chambre=''):
        print('StudentController.get_filtered_students called')
        students = self.list_students()
        # Filter by type_section if set
        if type_section:
            students = [s for s in students if s.get('type_section') == type_section]
        # Filter by keyword if set
        if keyword:
            students = [s for s in students if keyword.lower() in (s.get('nom','').lower() + s.get('prenom','').lower() + s.get('matricule','').lower())]
        # Filter by chambre if set
        if chambre:
            students = [s for s in students if (s.get('num_chambre') == chambre) or (chambre == 'Aucune' and (s.get('num_chambre') in [None, '', 'no room']))]
        # Mark 'Aucune' for students with no room for display, and add pavillon
        from controllers.room_controller import RoomController
        rooms = RoomController().list_rooms()
        for s in students:
            if s.get('num_chambre') in [None, '', 'no room']:
                s['num_chambre'] = 'Aucune'
                s['pavilion'] = 'Aucune'
            else:
                room = next((r for r in rooms if r.get('room_number') == s['num_chambre']), None)
                s['pavilion'] = room['pavilion'] if room else ''
        return students
