import io
import pandas as pd
from flask import send_file
from io import BytesIO
from datetime import datetime

def generate_sample_students_xlsx():
    """Generate a sample XLSX file with student data compatible with the DB import logic."""
    data = {
        'matricule': [f'STU{i:03d}' for i in range(1, 6)],
        'nom': ['Dupont', 'Martin', 'Bernard', 'Petit', 'Robert'],
        'prenom': ['Jean', 'Marie', 'Pierre', 'Sophie', 'Paul'],
        'sexe': ['M', 'F', 'M', 'F', 'M'],
        'cin': [f'CIN{i:06d}' for i in range(1, 6)],
        'date_naissance': ['0001-01-01']*5,
        'nationalite': ['Marocaine']*5,
        'telephone': [f'06{i:08d}' for i in range(10000001, 10000006)],
        'email': [f'etudiant{i}@example.com' for i in range(1, 6)],
        'annee_universitaire': ['2023/2024']*5,
        'filiere_id': [1, 2, 3, 4, 5],
        'dossier_medicale': ['RAS']*5,
        'observation': ['']*5,
        'photo': ['']*5,
        'laureat': ['']*5,
        'num_chambre': ['A101', 'B202', '', '', ''],
        'mobilite': ['']*5,
        'vie_associative': ['']*5,
        'bourse': ['Oui', 'Non', 'Oui', 'Non', 'Oui'],
        'type_section': ['IAV', 'APESA', 'IAV', 'APESA', 'IAV']
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='students', index=False)
        workbook = writer.book
        worksheet = writer.sheets['students']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D4EDDA', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='sample_students.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def generate_sample_rooms_xlsx():
    """Generate a sample XLSX file with room data compatible with the DB import logic."""
    data = {
        'room_number': [f'A{i:03d}' for i in range(1, 6)],
        'pavilion': ['A', 'B', 'C', 'D', 'E'],
        'room_type': ['single', 'double', 'triple', 'double', 'single'],
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='rooms', index=False)
        workbook = writer.book
        worksheet = writer.sheets['rooms']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D4EDDA', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='sample_rooms.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def generate_sample_filieres_xlsx():
    """Generate a sample XLSX file with filiere data compatible with the DB import logic."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Génie Informatique', 'Génie Civil', 'Génie Électrique', 'Génie Mécanique', 'Génie Industriel']
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='filieres', index=False)
        workbook = writer.book
        worksheet = writer.sheets['filieres']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D4EDDA', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='sample_filieres.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
