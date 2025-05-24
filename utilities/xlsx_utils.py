# utilities/xlsx_utils.py
import io
import pandas as pd
from flask import send_file

def export_xlsx(data, filename='students.xlsx'):
    # Prepare data for export with the same columns as PDF
    rows = []
    for student in data:
        nom_complet = f"{student.get('nom', '')} {student.get('prenom', '')}"
        type_section = student.get('type_section', '') or 'Non spécifié'
        annee_universitaire = student.get('annee_universitaire', '') or 'Non spécifiée'
        num_chambre = student.get('num_chambre') if student.get('num_chambre') not in [None, '', 'no room'] else 'Aucune'
        rows.append({
            'Matricule': student.get('matricule', ''),
            'Nom Complet': nom_complet,
            'Type Internat': type_section,
            'Année universitaire': annee_universitaire,
            'Chambre': num_chambre
        })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    # Always force the correct extension and mimetype
    filename = filename.rsplit('.', 1)[0] + '.xlsx'
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def import_xlsx(file):
    df = pd.read_excel(file)
    return df.to_dict(orient='records')
