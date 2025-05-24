import io
import pandas as pd
from flask import send_file
from io import BytesIO
from datetime import datetime, timedelta
import random

def generate_sample_students_xlsx():
    """Generate a sample XLSX file with student data."""
    # Create sample data
    data = {
        'Matricule': [f'STU{i:03d}' for i in range(1, 6)],
        'Nom': ['Dupont', 'Martin', 'Bernard', 'Petit', 'Robert'],
        'Prénom': ['Jean', 'Marie', 'Pierre', 'Sophie', 'Paul'],
        'CNE': [f'CNE{i:06d}' for i in range(1, 6)],
        'CIN': [f'CIN{i:06d}' for i in range(1, 6)],
        'Date de naissance': [(datetime.now() - timedelta(days=random.randint(365*18, 365*25))).strftime('%Y-%m-%d') for _ in range(5)],
        'Lieu de naissance': ['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille'],
        'Adresse': ['123 Rue Example', '456 Avenue Test', '789 Boulevard Demo', '321 Rue Sample', '654 Avenue Demo'],
        'Téléphone': [f'06{random.randint(10000000, 99999999)}' for _ in range(5)],
        'Email': [f'etudiant{i}@example.com' for i in range(1, 6)],
        'Filière': ['Génie Informatique', 'Génie Civil', 'Génie Électrique', 'Génie Mécanique', 'Génie Industriel']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Étudiants', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Étudiants']
        
        # Add some formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D4EDDA',
            'border': 1
        })
        
        # Write headers with format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)  # Set column width
    
    output.seek(0)
    return output

def generate_sample_rooms_xlsx():
    """Generate a sample XLSX file with room data."""
    # Create sample data
    data = {
        'Numéro': [f'CH{i:03d}' for i in range(1, 6)],
        'Pavillon': ['A', 'B', 'C', 'D', 'E'],
        'Type': ['Simple', 'Double', 'Triple', 'Double', 'Simple'],
        'Capacité': [1, 2, 3, 2, 1],
        'Occupée': ['Non', 'Oui', 'Non', 'Oui', 'Non']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Chambres', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Chambres']
        
        # Add some formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D4EDDA',
            'border': 1
        })
        
        # Write headers with format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)  # Set column width
    
    output.seek(0)
    return output
