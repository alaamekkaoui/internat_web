# routes/student_route.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from controllers.student_controller import StudentController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf
from utils.decorators import login_required, role_required # Corrected path
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utilities.file_utils import handle_file_upload
from controllers.filiere_controller import FiliereController
from controllers.room_controller import RoomController
student_bp = Blueprint('student', __name__)
student_controller = StudentController()

@student_bp.route('/students', methods=['GET'])
def list_students():
    result = student_controller.list_students()
    if 'error' in result:
        flash(result['error'], 'danger')
        return render_template('student/list.html', students=[])
    return render_template('student/list.html', students=result)

@student_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    filieres = FiliereController().list_filieres()
    rooms = RoomController().list_rooms()
    if request.method == 'POST':
        data = request.form
        result = student_controller.add_student(data, request.files)
        if 'error' in result:
            flash(result['error'], 'danger')
            return render_template('student/add.html', filieres=filieres, rooms=rooms)
        flash('Student added successfully!', 'success')
        return redirect(url_for('student.list_students'))
    return render_template('student/add.html', filieres=filieres, rooms=rooms)

@student_bp.route('/students/<int:student_id>', methods=['GET'])
def student_profile(student_id):
    result = student_controller.get_student(student_id)
    filieres = FiliereController().list_filieres()
    rooms = RoomController().list_rooms()
    if 'error' in result:
        flash(result['error'], 'danger')
        return redirect(url_for('student.list_students'))
    return render_template('student/profile.html', student=result, filieres=filieres, rooms=rooms)

@student_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@login_required
# @role_required('admin') # Uncomment if only admins can delete
def delete_student(student_id):
    try:
        result = student_controller.delete_student(student_id)
        if 'error' in result:
            flash(result['error'], 'danger')
            return redirect(url_for('student.list_students'))
        flash('Student deleted successfully!', 'success')
        return redirect(url_for('student.list_students'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.list_students'))

@student_bp.route('/students/export/xlsx', methods=['GET'])
def export_students_xlsx():
    try:
        students = student_controller.list_students()
        folder = 'static/xlsx'
        os.makedirs(folder, exist_ok=True)
        filename = 'students.xlsx'
        return export_xlsx(students, filename, folder)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.list_students'))

@student_bp.route('/students/import/xlsx', methods=['POST'])
@login_required # Assuming import is a modification action
def import_students_xlsx():
    try:
        file = request.files['file']
        data = import_xlsx(file)
        for student in data:
            student_controller.add_student(student)
        flash('Students imported successfully!', 'success')
        return redirect(url_for('student.list_students'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.list_students'))

@student_bp.route('/students/export/pdf', methods=['GET'])
def export_students_pdf():
    try:
        # Get all students
        students = student_controller.list_students()
        if isinstance(students, dict) and 'error' in students:
            flash(students['error'], 'danger')
            return redirect(url_for('student.list_students'))

        # Create PDF directory if it doesn't exist
        pdf_dir = 'static/pdfs'
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, 'students.pdf')

        # Generate PDF
        pdf_file = export_pdf(students, pdf_path)
        if not pdf_file:
            flash('Error generating PDF', 'danger')
            return redirect(url_for('student.list_students'))

        # Return the PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name='students.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.list_students'))

@student_bp.route('/students/<int:student_id>/upload-image', methods=['POST'])
@login_required # Modifies student data
def upload_student_image(student_id):
    try:
        # Get student info
        student = student_controller.get_student(student_id)
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('student.list_students'))

        # Handle file upload
        upload_dir = os.path.join('static', 'uploads')
        filename_prefix = f"{student['nom']}_{student['prenom']}"
        
        result = handle_file_upload(
            file=request.files.get('image'),
            upload_dir=upload_dir,
            filename_prefix=filename_prefix
        )

        if not result['success']:
            flash(result['error'], 'danger')
            return redirect(url_for('student.student_profile', student_id=student_id))

        # Update student record with image filename
        try:
            update_result = student_controller.update_student_image(student_id, result['filename'])
            if 'error' in update_result:
                flash(update_result['error'], 'danger')
            else:
                flash('Image uploaded successfully!', 'success')
        except Exception as e:
            flash('Error updating student record', 'danger')
            return redirect(url_for('student.student_profile', student_id=student_id))

        return redirect(url_for('student.student_profile', student_id=student_id))

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect(url_for('student.student_profile', student_id=student_id))

@student_bp.route('/students/<int:student_id>/modify', methods=['GET', 'POST'])
@login_required
def modify_student(student_id):
    from controllers.filiere_controller import FiliereController
    from controllers.room_controller import RoomController
    filieres = FiliereController().list_filieres()
    rooms = RoomController().list_rooms()
    if request.method == 'POST':
        data = request.form
        result = student_controller.update_student(student_id, data, request.files)
        if 'error' in result:
            flash(result['error'], 'danger')
            student = student_controller.get_student(student_id)
            return render_template('student/edit.html', student=student, filieres=filieres, rooms=rooms)
        flash('Student updated successfully!', 'success')
        return redirect(url_for('student.list_students'))
    # GET request - show edit form
    student = student_controller.get_student(student_id)
    if 'error' in student:
        flash(student['error'], 'danger')
        return redirect(url_for('student.list_students'))
    # Ensure student is an object with attribute access for Jinja
    class StudentObj(dict):
        def __getattr__(self, item):
            return self.get(item)
    student_obj = StudentObj(student)
    return render_template('student/edit.html', student=student_obj, filieres=filieres, rooms=rooms)

@student_bp.route('/students/<int:student_id>/download-pdf', methods=['GET'])
def download_pdf(student_id):
    # You should implement PDF generation logic here. For now, serve a static or pre-generated PDF.
    pdf_path = f'static/pdfs/student_{student_id}.pdf'
    if not os.path.exists(pdf_path):
        flash('PDF non trouvé pour cet étudiant.', 'danger')
        return redirect(url_for('student.list_students'))
    return export_pdf(pdf_path)
