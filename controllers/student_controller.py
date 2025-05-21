# controllers/student_controller.py
from models.student import Student
from datetime import datetime
from utilities.file_utils import handle_file_upload
import os

class StudentController:
    def __init__(self):
        self.student_model = Student()

    def list_students(self):
        try:
            students = self.student_model.get_all_students()
            return students
        except Exception as e:
            return {'error': str(e)}

    def add_student(self, data, files=None):
        try:
            # Convert ImmutableMultiDict to regular dictionary
            data_dict = dict(data)
            
            # Handle file upload if present
            if files and 'photo' in files and files['photo'].filename:
                # Get file extension and convert to lowercase
                file_ext = os.path.splitext(files['photo'].filename)[1].lower()
                # Convert to jpg if it's jpeg, otherwise use png
                if file_ext == '.jpeg':
                    file_ext = '.jpg'
                elif file_ext not in ['.jpg', '.png']:
                    file_ext = '.jpg'  # Default to jpg for other formats
                
                # Create filename with lastname_firstname.extension
                filename = f"{data_dict.get('nom')}_{data_dict.get('prenom')}{file_ext}"
                
                result = handle_file_upload(
                    file=files['photo'],
                    filename_prefix=filename,
                    upload_dir='static/uploads'
                )
                
                if result['success']:
                    data_dict['photo'] = filename  # Store just the filename without path
                else:
                    return {'error': result['error']}

            # Map form data to match database fields
            student_data = {
                'nom': data_dict.get('nom') or data_dict.get('lastname'),
                'prenom': data_dict.get('prenom') or data_dict.get('firstname'),
                'sexe': data_dict.get('sexe') or data_dict.get('gender'),
                'matricule': data_dict.get('matricule'),
                'cin': data_dict.get('cin'),
                'date_naissance': data_dict.get('date_naissance') or data_dict.get('birth_date'),
                'nationalite': data_dict.get('nationalite') or data_dict.get('nationality'),
                'telephone': data_dict.get('telephone') or data_dict.get('phone'),
                'email': data_dict.get('email'),
                'annee_universitaire': data_dict.get('annee_universitaire') or data_dict.get('academic_year'),
                'filiere_id': data_dict.get('filiere_id'),
                'dossier_medicale': data_dict.get('dossier_medicale') or data_dict.get('medical_record'),
                'observation': data_dict.get('observation'),
                'photo': data_dict.get('photo'),
                'laureat': data_dict.get('laureat', 'non'),
                'num_chambre': data_dict.get('num_chambre') or data_dict.get('room_number'),
                'mobilite': data_dict.get('mobilite', 'non'),
                'vie_associative': data_dict.get('vie_associative', 'non'),
                'bourse': data_dict.get('bourse', 'non'),
                'type_section': data_dict.get('type_section', 'APESA')
            }

            # Validate type_section
            if student_data['type_section'] not in ['APESA', 'IAV', 'INTERNA']:
                raise Exception("Type/Section must be either 'APESA', 'IAV', or 'INTERNA'")

            # Validate required fields
            required_fields = ['nom', 'prenom', 'sexe', 'matricule', 'cin', 'date_naissance', 
                             'nationalite', 'telephone', 'email', 'annee_universitaire', 
                             'filiere_id', 'dossier_medicale', 'bourse']
            
            missing_fields = [field for field in required_fields if not student_data.get(field)]
            if missing_fields:
                raise Exception(f"Missing required fields: {', '.join(missing_fields)}")

            # Add student to database
            student_id = self.student_model.add_student(student_data)
            return {'student_id': student_id}
        except Exception as e:
            return {'error': str(e)}

    def get_student(self, student_id):
        try:
            student = self.student_model.get_student(student_id)
            if not student:
                return {'error': 'Student not found'}
            return student
        except Exception as e:
            return {'error': str(e)}

    def update_student(self, student_id, data, files=None):
        try:
            # Convert ImmutableMultiDict to regular dictionary
            data_dict = dict(data)
            
            # Handle file upload if present
            if files and 'photo' in files and files['photo'].filename:
                # Get file extension and convert to lowercase
                file_ext = os.path.splitext(files['photo'].filename)[1].lower()
                # Convert to jpg if it's jpeg, otherwise use png
                if file_ext == '.jpeg':
                    file_ext = '.jpg'
                elif file_ext not in ['.jpg', '.png']:
                    file_ext = '.jpg'  # Default to jpg for other formats
                
                # Create filename with lastname_firstname.extension
                filename = f"{data_dict.get('nom')}_{data_dict.get('prenom')}{file_ext}"
                
                result = handle_file_upload(
                    file=files['photo'],
                    filename_prefix=filename,
                    upload_dir='static/uploads'
                )
                
                if result['success']:
                    data_dict['photo'] = filename  # Store just the filename without path
                else:
                    return {'error': result['error']}

            # Map form data to match database fields
            student_data = {
                'nom': data_dict.get('nom') or data_dict.get('lastname'),
                'prenom': data_dict.get('prenom') or data_dict.get('firstname'),
                'sexe': data_dict.get('sexe') or data_dict.get('gender'),
                'matricule': data_dict.get('matricule'),
                'cin': data_dict.get('cin'),
                'date_naissance': data_dict.get('date_naissance') or data_dict.get('birth_date'),
                'nationalite': data_dict.get('nationalite') or data_dict.get('nationality'),
                'telephone': data_dict.get('telephone') or data_dict.get('phone'),
                'email': data_dict.get('email'),
                'annee_universitaire': data_dict.get('annee_universitaire') or data_dict.get('academic_year'),
                'filiere_id': data_dict.get('filiere_id'),
                'dossier_medicale': data_dict.get('dossier_medicale') or data_dict.get('medical_record'),
                'observation': data_dict.get('observation'),
                'photo': data_dict.get('photo'),
                'laureat': data_dict.get('laureat'),
                'num_chambre': data_dict.get('num_chambre') or data_dict.get('room_number'),
                'mobilite': data_dict.get('mobilite'),
                'vie_associative': data_dict.get('vie_associative'),
                'bourse': data_dict.get('bourse'),
                'type_section': data_dict.get('type_section')
            }

            # Remove None values
            student_data = {k: v for k, v in student_data.items() if v is not None}

            # Validate type_section if it's being updated
            if 'type_section' in student_data and student_data['type_section'] not in ['APESA', 'IAV', 'INTERNA']:
                raise Exception("Type/Section must be either 'APESA', 'IAV', or 'INTERNA'")

            # Update student in database
            self.student_model.update_student(student_id, student_data)
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}

    def delete_student(self, student_id):
        try:
            self.student_model.delete_student(student_id)
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}

    def update_student_image(self, student_id, filename):
        try:
            self.student_model.update_student_image(student_id, filename)
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}

    def search_students(self, keyword=None, chambre=None):
        try:
            students = self.student_model.search_students(keyword, chambre)
            return students
        except Exception as e:
            return {'error': str(e)}
