from flask import Blueprint, render_template
from models import Student, Filiere, Room

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    # Get total counts
    total_students = Student().get_all_students()
    total_filieres = Filiere().get_all_filieres()
    total_rooms = Room().get_all_rooms()
    
    # Calculate statistics
    occupied_rooms = len([room for room in total_rooms if room['is_used']])
    available_rooms = len([room for room in total_rooms if not room['is_used']])
    internal_students = len([student for student in total_students if student['type_section'] == 'Interne'])
    external_students = len([student for student in total_students if student['type_section'] == 'Externe'])
    
    return render_template('home.html',
                         total_students=len(total_students),
                         total_filieres=len(total_filieres),
                         total_rooms=len(total_rooms),
                         occupied_rooms=occupied_rooms,
                         available_rooms=available_rooms,
                         internal_students=internal_students,
                         external_students=external_students) 