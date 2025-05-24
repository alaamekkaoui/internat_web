# controllers/home_controller.py
from models import Student, Filiere, Room

class HomeController:
    def get_dashboard_stats(self):
        print('HomeController.get_dashboard_stats called')
        total_students = Student().get_all_students()
        total_filieres = Filiere().get_all_filieres()
        total_rooms = Room().get_all_rooms()
        occupied_rooms = len([room for room in total_rooms if room['is_used']])
        available_rooms = len([room for room in total_rooms if not room['is_used']])
        iav_students = len([student for student in total_students if student['type_section'] == 'IAV'])
        apesa_students = len([student for student in total_students if student['type_section'] == 'APESA'])
        return {
            'total_students': len(total_students),
            'total_filieres': len(total_filieres),
            'total_rooms': len(total_rooms),
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'iav_students': iav_students,
            'apesa_students': apesa_students
        }
