import io
import pandas as pd
from flask import send_file

def generate_sample_students_xlsx():
    """Generate a sample students XLSX file in-memory with French headers matching the DB."""
    data = [
        {
            'matricule': '12345',
            'cin': 'AB123456',
            'nom': 'Ali',
            'prenom': 'Benali',
            'date_naissance': '2000-01-01',
            'sexe': 'homme',
            'nationalite': 'Marocain',
            'telephone': '0612345678',
            'email': 'ali.benali@example.com',
            'annee_universitaire': '2024/2025',
            'filiere_id': 1,
            'dossier_medicale': '',
            'observation': 'Remarque test',
            'laureat': 'non',
            'num_chambre': '101',
            'mobilite': 'oui',
            'vie_associative': 'oui',
            'bourse': 'non',
            'photo': '',
            'type_section': 'IAV',
        },
        {
            'matricule': '23456',
            'cin': 'CD234567',
            'nom': 'Sara',
            'prenom': 'El Amrani',
            'date_naissance': '2001-02-02',
            'sexe': 'femme',
            'nationalite': 'Marocaine',
            'telephone': '0623456789',
            'email': 'sara.elamrani@example.com',
            'annee_universitaire': '2024/2025',
            'filiere_id': 2,
            'dossier_medicale': '',
            'observation': 'Observation',
            'laureat': 'oui',
            'num_chambre': '102',
            'mobilite': 'non',
            'vie_associative': 'oui',
            'bourse': 'oui',
            'photo': '',
            'type_section': 'APESA',
        },
        {
            'matricule': '34567',
            'cin': 'EF345678',
            'nom': 'Mehdi',
            'prenom': 'Ouazzani',
            'date_naissance': '2002-03-03',
            'sexe': 'homme ',
            'nationalite': 'Marocain',
            'telephone': '0634567890',
            'email': 'mehdi.ouazzani@example.com',
            'annee_universitaire': '2024/2025',
            'filiere_id': 3,
            'dossier_medicale': '',
            'observation': 'Aucune remarque',
            'laureat': 'non',
            'num_chambre': '',
            'mobilite': 'oui',
            'vie_associative': 'non',
            'bourse': 'non',
            'photo': '',
            'type_section': '',
        },
    ]
    df = pd.DataFrame(data)
    # Replace NaN/None/empty with empty string for all columns
    df = df.fillna("")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='sample_students.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
