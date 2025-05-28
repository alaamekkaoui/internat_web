# routes/student_route.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from controllers.student_controller import StudentController
from utilities.xlsx_utils import export_xlsx, import_xlsx
from utilities.pdf_utils import export_pdf, generate_student_pdf
from utils.decorators import login_required, role_required # Corrected path
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utilities.file_utils import handle_file_upload
from controllers.filiere_controller import FiliereController
from controllers.room_controller import RoomController
from utilities.sample_utils import generate_sample_students_xlsx
from math import isnan

student_bp = Blueprint('student', __name__)
student_controller = StudentController()

@student_bp.route('/students', methods=['GET'])
def list_students():
    print('student_route.list_students called')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of students per page
    
    # Get filter parameters
    search = request.args.get('keyword', '')
    filiere_id = request.args.get('filiere', type=int)
    internat = request.args.get('type_section', '')
    pavilion = request.args.get('pavilion', '')
    chambre = request.args.get('chambre', '')
    
    # Get paginated students
    students, total = student_controller.get_paginated_students(
        page=page,
        per_page=per_page,
        search=search,
        filiere_id=filiere_id,
        internat=internat,
        pavilion=pavilion,
        chambre=chambre
    )
    
    # Create custom pagination object
    class Pagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None

        def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (num > self.page - left_current - 1 and
                     num < self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=total,
        items=students
    )
    
    # Get filieres for the filter dropdown
    filieres = FiliereController().list_filieres()
    
    return render_template('student/list.html', 
                         students=students,
                         pagination=pagination,
                         filieres=filieres)

@student_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    print('student_route.add_student called')
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
    print('student_route.student_profile called')
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
    print('student_route.delete_student called')
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
    print('student_route.export_students_xlsx called')
    try:
        students = student_controller.list_students()
        return export_xlsx(students, filename='students.xlsx')
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.list_students'))

@student_bp.route('/students/import/xlsx', methods=['POST'])
@login_required
def import_students_xlsx():
    print('student_route.import_students_xlsx called')
    file = request.files['file']
    data = import_xlsx(file)
    # All fields are now optional for import
    imported_count = 0
    from controllers.student_controller import StudentController
    from controllers.filiere_controller import FiliereController
    from controllers.room_controller import RoomController
    student_controller = StudentController()
    filiere_controller = FiliereController()
    room_controller = RoomController()
    filieres_by_id = {str(f['id']): f['id'] for f in filiere_controller.list_filieres()}
    rooms_by_num = {str(r['room_number']): r['room_number'] for r in room_controller.list_rooms()}
    imported_students = []
    failed_students = []
    for student in data:
        # If filiere_id not found, set to empty string
        filiere_id_val = str(student.get('filiere_id', '')).strip()
        if not filiere_id_val or filiere_id_val not in filieres_by_id:
            student['filiere_id'] = ''
        else:
            student['filiere_id'] = filieres_by_id[filiere_id_val]
        # If num_chambre not found, set to empty string
        num_chambre_val = str(student.get('num_chambre', '')).strip()
        if num_chambre_val and num_chambre_val not in rooms_by_num:
            student['num_chambre'] = ''
        # If date_naissance missing, set to default
        if not student.get('date_naissance'):
            student['date_naissance'] = '0001-01-01'
        try:
            result = student_controller.add_student(student)
            if isinstance(result, dict) and result.get('error'):
                failed_students.append(f"<b>{student.get('nom', '')} {student.get('prenom', '')} (Matricule: {student.get('matricule', 'inconnu')})</b> - erreur: {result['error']}")
            else:
                imported_students.append(f"<b>{student.get('nom', '')} {student.get('prenom', '')} (Matricule: {student.get('matricule', 'inconnu')})</b>")
                imported_count += 1
        except Exception as e:
            failed_students.append(f"<b>{student.get('nom', '')} {student.get('prenom', '')} (Matricule: {student.get('matricule', 'inconnu')})</b> - erreur technique: {e}")
    msg = f"<b>{imported_count} étudiant(s) importé(s) avec succès !</b>"
    if imported_students:
        msg += '<br><u>Étudiants ajoutés :</u><ul>' + ''.join(f'<li>{s}</li>' for s in imported_students) + '</ul>'
    if failed_students:
        msg += '<br><u>Étudiants non ajoutés ou partiellement ajoutés :</u><ul>' + ''.join(f'<li>{s}</li>' for s in failed_students) + '</ul>'
        flash(msg, 'warning')
    else:
        flash(msg, 'success')
    return redirect(url_for('student.list_students'))

@student_bp.route('/students/export/pdf', methods=['GET'])
def export_students_pdf():
    print('student_route.export_students_pdf called')
    try:
        students = student_controller.list_students()
        if isinstance(students, dict) and 'error' in students:
            flash(students['error'], 'danger')
            return redirect(url_for('student.list_students'))
        from utilities.pdf_utils import export_pdf
        pdf_buffer = export_pdf(students)
        if not pdf_buffer:
            flash('Error generating PDF', 'danger')
            return redirect(url_for('student.list_students'))
        return send_file(
            pdf_buffer,
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
    print('student_route.upload_student_image called')
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
    print('student_route.modify_student called')
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
        return redirect(url_for('student.student_profile', student_id=student_id))
    # GET request - show edit form
    student = student_controller.get_student(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('student.list_students'))
    return render_template('student/edit.html', student=student, filieres=filieres, rooms=rooms)

@student_bp.route('/students/<int:student_id>/download-pdf', methods=['GET'])
def download_pdf(student_id):
    print('student_route.download_pdf called')
    # You should implement PDF generation logic here. For now, serve a static or pre-generated PDF.
    pdf_path = f'static/pdfs/student_{student_id}.pdf'
    if not os.path.exists(pdf_path):
        flash('PDF non trouvé pour cet étudiant.', 'danger')
        return redirect(url_for('student.list_students'))
    return export_pdf(pdf_path)

@student_bp.route('/<int:student_id>/export-pdf')
def export_pdf(student_id):
    print('student_route.export_pdf called')
    """Export student profile as PDF"""
    try:
        student = StudentController().get_student(student_id)
        if not student:
            flash('Étudiant non trouvé', 'error')
            return redirect(url_for('student.list_students'))

        # Generate PDF
        pdf_path = generate_student_pdf(student)
        
        # Send the PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"profil_{student['nom']}_{student['prenom']}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'error')
        return redirect(url_for('student.profile', student_id=student_id))

@student_bp.route('/students/sample-xlsx', methods=['GET'])
def download_sample_students_xlsx():
    print('student_route.download_sample_students_xlsx called')
    return generate_sample_students_xlsx()
