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
        result = self.student_model.add_student(data_dict)
        print(f'[DEBUG] StudentController.add_student result: {result}')
        if result is False or result is None:
            return {'error': 'Add failed'}
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
        result = self.student_model.update_student(student_id, data_dict)
        print(f'[DEBUG] StudentController.update_student result: {result}')
        if result is False:
            return {'error': 'Update failed'}
        return {'status': 'success'}

    def delete_student(self, student_id):
        return self.student_model.delete_student(student_id)

    def update_student_image(self, student_id, filename):
        return self.student_model.update_student_image(student_id, filename)

    def search_students(self, keyword=None, chambre=None):
        return self.student_model.search_students(keyword, chambre)
