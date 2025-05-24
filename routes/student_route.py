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
    # Get filter params
    type_section = request.args.get('type_section', '')
    keyword = request.args.get('keyword', '')
    chambre = request.args.get('chambre', '')
    students = student_controller.list_students()
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
    for s in students:
        if s.get('num_chambre') in [None, '', 'no room']:
            s['num_chambre'] = 'Aucune'
            s['pavilion'] = ''
        else:
            # Find the room to get the pavilion
            from controllers.room_controller import RoomController
            rooms = RoomController().list_rooms()
            room = next((r for r in rooms if r.get('room_number') == s['num_chambre']), None)
            s['pavilion'] = room['pavilion'] if room else ''
    return render_template('student/list.html', students=students)

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
        return export_xlsx(students, filename='students.xlsx')
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.list_students'))

@student_bp.route('/students/import/xlsx', methods=['POST'])
@login_required
def import_students_xlsx():
    from utilities.xlsx_utils import import_xlsx
    file = request.files['file']
    data = import_xlsx(file)
    required_fields = ['matricule', 'nom', 'prenom', 'type_section', 'annee_universitaire']  # filiere is optional
    errors = []
    imported_count = 0
    from controllers.student_controller import StudentController
    from controllers.filiere_controller import FiliereController
    student_controller = StudentController()
    filiere_controller = FiliereController()
    filieres_by_name = {str(f['name']).strip().lower(): f['id'] for f in filiere_controller.list_filieres()}
    filieres_by_id = {str(f['id']): f['id'] for f in filiere_controller.list_filieres()}
    imported_students = []
    failed_students = []
    for student in data:
        # Check for filiere_id in the row
        filiere_id_val = str(student.get('filiere_id', '')).strip()
        filiere_id = None
        if filiere_id_val.isdigit() and filiere_id_val in filieres_by_id:
            filiere_id = filieres_by_id[filiere_id_val]
        else:
            # If not valid id, try by filiere name
            filiere_val = str(student.get('filiere', '')).strip()
            if filiere_val:
                filiere_id = filieres_by_name.get(filiere_val.lower())
        student['filiere_id'] = filiere_id if filiere_id else None
        # Normalize sexe
        sexe_val = str(student.get('sexe', '')).strip().lower()
        if sexe_val in ['m', 'homme', 'male', '1']:
            student['sexe'] = 'M'
        elif sexe_val in ['f', 'femme', 'female', '2']:
            student['sexe'] = 'F'
        else:
            student['sexe'] = None
        # Check required fields
        missing = [field for field in required_fields if not student.get(field)]
        if missing:
            failed_students.append(f"<b>{student.get('nom', '')} {student.get('prenom', '')} (Matricule: {student.get('matricule', 'inconnu')})</b> - informations manquantes: {', '.join(missing)}")
            continue
        if not student['filiere_id'] and (student.get('filiere') or filiere_id_val):
            failed_students.append(f"<b>{student.get('nom', '')} {student.get('prenom', '')} (Matricule: {student.get('matricule', 'inconnu')})</b> - filière '{student.get('filiere', '') or filiere_id_val}' non trouvée.")
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
        return redirect(url_for('student.student_profile', student_id=student_id))
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

@student_bp.route('/<int:student_id>/export-pdf')
def export_pdf(student_id):
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
    return generate_sample_students_xlsx()
