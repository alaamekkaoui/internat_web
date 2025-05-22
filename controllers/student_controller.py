# controllers/student_controller.py
from models.student import Student
from models.room import Room
from models.room_history import RoomHistory
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
            print(f"[DEBUG] add_student called with data: {data} and files: {files}")
            data_dict = dict(data)
            # Only require: nom, prenom, cin, matricule, date_naissance
            required_fields = ['nom', 'prenom', 'cin', 'matricule', 'date_naissance']
            for field in required_fields:
                val = data_dict.get(field)
                if not val or (field == 'date_naissance' and (val == '01/01/0001' or val == '0001-01-01')):
                    data_dict[field] = 'not found'
            # If no room is specified, set num_chambre to None or 'no room'
            if not data_dict.get('num_chambre'):
                data_dict['num_chambre'] = 'no room'
            # Map form data to match database fields (other fields optional)
            student_data = {
                'nom': data_dict.get('nom'),
                'prenom': data_dict.get('prenom'),
                'cin': data_dict.get('cin'),
                'matricule': data_dict.get('matricule'),
                'date_naissance': data_dict.get('date_naissance'),
                'nationalite': data_dict.get('nationalite'),
                'sexe': data_dict.get('sexe'),
                'telephone': data_dict.get('telephone'),
                'email': data_dict.get('email'),
                'annee_universitaire': data_dict.get('annee_universitaire'),
                'filiere_id': data_dict.get('filiere_id'),
                'dossier_medicale': data_dict.get('dossier_medicale'),
                'observation': data_dict.get('observation'),
                'photo': data_dict.get('photo'),
                'laureat': data_dict.get('laureat'),
                'num_chambre': data_dict.get('num_chambre'),
                'mobilite': data_dict.get('mobilite'),
                'vie_associative': data_dict.get('vie_associative'),
                'bourse': data_dict.get('bourse'),
                'type_section': data_dict.get('type_section')
            }

            print(f"[DEBUG] student_data to insert: {student_data}")
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
                    student_data['photo'] = filename  # Store just the filename without path
                else:
                    return {'error': result['error']}

            # Validate type_section
            if student_data['type_section'] not in ['APESA', 'IAV', 'INTERNA']:
                raise Exception("Type/Section must be either 'APESA', 'IAV', or 'INTERNA'")

            # Add student to database
            student_id = self.student_model.add_student(student_data)
            print(f"[DEBUG] student_id after insert: {student_id}")
            # Add to room history if a room is assigned
            if student_data.get('num_chambre') and student_data['num_chambre'] not in [None, '', 'no room']:
                print(f"[DEBUG] Adding to room history: student_id={student_id}, room={student_data['num_chambre']}")
                RoomHistory().add_history(student_id, student_data['num_chambre'])

            # --- Room capacity logic ---
            room_number = student_data.get('num_chambre')
            if room_number:
                room_model = Room()
                room_info = None
                # Find room by room_number
                all_rooms = room_model.get_all_rooms()
                for r in all_rooms:
                    if str(r[1]) == str(room_number):  # assuming r[1] is room_number
                        room_info = r
                        break
                if room_info:
                    capacity = int(room_info[4])  # assuming r[4] is capacity
                    student_count = room_model.get_student_count_in_room(room_number)
                    if student_count >= capacity:
                        room_model.set_room_used_status(room_number, True)
                    else:
                        room_model.set_room_used_status(room_number, False)
            print(f"[DEBUG] Room info for capacity logic: {room_info}")
            print(f"[DEBUG] Returning from add_student: {{'student_id': student_id}}")
            return {'student_id': student_id}
        except Exception as e:
            print(f"[ERROR] Exception in add_student: {e}")
            return {'error': str(e)}

    def get_student(self, student_id):
        try:
            print(f"[DEBUG] Fetching student with id: {student_id}")
            student = self.student_model.get_student_by_id(student_id)
            print(f"[DEBUG] Student fetched: {student}")
            if not student:
                print(f"[ERROR] Student with id {student_id} not found!")
                return {'error': 'Student not found'}
            # Defensive: ensure student is a dict
            if not isinstance(student, dict):
                print(f"[ERROR] student is not a dict: {student}")
                return {'error': 'Student data is invalid'}
            # Get room info
            room = None
            if student.get('num_chambre') and student['num_chambre'] not in [None, '', 'no room']:
                room_model = Room()
                all_rooms = room_model.get_all_rooms()
                print(f"[DEBUG] All rooms: {all_rooms}")
                for r in all_rooms:
                    if str(r[1]) == str(student['num_chambre']):
                        room = {
                            'room_number': r[1],
                            'pavilion': r[2],
                            'room_type': r[3],
                            'capacity': r[4],
                            'is_used': r[5],
                            'id': r[0]
                        }
                        break
            # Get room history from RoomHistory model
            try:
                history_raw = RoomHistory().get_history_for_student(student_id)
            except Exception as herr:
                print(f"[ERROR] Exception fetching room history: {herr}")
                history_raw = []
            print(f"[DEBUG] Room history raw: {history_raw}")
            history = []
            all_rooms = Room().get_all_rooms()
            for h in history_raw:
                try:
                    rh = {'year': h[3], 'room': None}
                    for r in all_rooms:
                        if str(r[0]) == str(h[2]) or str(r[1]) == str(h[2]):
                            rh['room'] = {
                                'room_number': r[1],
                                'pavilion': r[2],
                                'room_type': r[3],
                                'capacity': r[4],
                                'is_used': r[5],
                                'id': r[0]
                            }
                            break
                    history.append(rh)
                except Exception as herr2:
                    print(f"[ERROR] Exception processing room history row: {herr2}")
            student['room'] = room
            student['history'] = history
            # Ensure 'id' is present for Jinja templates
            if 'id' not in student or student.get('id', None) is None:
                student['id'] = student_id
            print(f"[DEBUG] Final student dict for template: {student}")
            return student
        except Exception as e:
            print(f"[ERROR] Exception in get_student: {e}")
            return {'error': f'Error fetching student: {e}'}

    def update_student(self, student_id, data, files=None):
        try:
            print(f"[DEBUG] update_student called for id={student_id} with data: {data} and files: {files}")
            data_dict = dict(data)
            # If no room is specified, set num_chambre to 'no room'
            if not data_dict.get('num_chambre'):
                data_dict['num_chambre'] = 'no room'

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

            print(f"[DEBUG] student_data to update: {student_data}")
            self.student_model.update_student(student_id, student_data)
            print(f"[DEBUG] Updated student in DB for id={student_id}")
            # Add to room history if a room is assigned and not 'no room'
            if student_data.get('num_chambre') and student_data['num_chambre'] not in [None, '', 'no room']:
                print(f"[DEBUG] Adding to room history: student_id={student_id}, room={student_data['num_chambre']}")
                RoomHistory().add_history(student_id, student_data['num_chambre'])
            print(f"[DEBUG] Returning from update_student: {{'status': 'success'}}")
            return {'status': 'success'}
        except Exception as e:
            print(f"[ERROR] Exception in update_student: {e}")
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
