# utilities/pdf_utils.py
import io
import os
from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import tempfile

def export_pdf(data):
    """Generate a PDF file with student data and IAV logo, return as BytesIO."""
    import io
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from datetime import datetime
    import os
    buffer = io.BytesIO()
    try:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        content = []
        logo_path = os.path.join(os.path.dirname(__file__), '../static/images/iav.png')
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.5*inch, height=1.5*inch)
            img.hAlign = 'CENTER'
            content.append(img)
            content.append(Spacer(1, 12))
        content.append(Paragraph("Liste des Étudiants", title_style))
        content.append(Spacer(1, 20))
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray
        )
        content.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
        content.append(Spacer(1, 20))
        table_data = [['Matricule', 'Nom Complet', 'Type Internat', 'Année universitaire', 'Chambre']]
        for student in data:
            nom_complet = f"{student.get('nom', '')} {student.get('prenom', '')}"
            type_section = student.get('type_section', '') or 'Non spécifié'
            annee_universitaire = student.get('annee_universitaire', '') or 'Non spécifiée'
            num_chambre = student.get('num_chambre') if student.get('num_chambre') not in [None, '', 'no room'] else 'Aucune'
            table_data.append([
                student.get('matricule', ''),
                nom_complet,
                type_section,
                annee_universitaire,
                num_chambre
            ])
        table = Table(table_data, colWidths=[1.2*inch, 2.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(table)
        doc.build(content)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def save_pdf(pdf_folder, filename, pdf_stream):
    """Save a PDF stream to a file."""
    pdf_path = os.path.join(pdf_folder, filename)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_stream.read())
    return pdf_path

def generate_student_pdf(student):
    """Generate a PDF file for student profile"""
    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"student_profile_{student['id']}.pdf")
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Add IAV logo at the top
    logo_path = os.path.join(os.path.dirname(__file__), '../static/images/iav.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 12))
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    elements.append(Paragraph(f"Profil de l'étudiant", title_style))
    elements.append(Spacer(1, 20))
    
    # Add student photo if exists
    if student.get('photo'):
        photo_path = os.path.join('static', 'uploads', student['photo'])
        if os.path.exists(photo_path):
            img = Image(photo_path, width=2*inch, height=2*inch)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 20))
    
    # Add student name and matricule
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=10,
        alignment=1
    )
    elements.append(Paragraph(f"{student['prenom']} {student['nom']}", name_style))
    elements.append(Paragraph(f"Matricule: {student['matricule']}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Personal Information
    elements.append(Paragraph("Informations personnelles", styles['Heading2']))
    personal_data = [
        ['Nom:', student['nom']],
        ['Prénom:', student['prenom']],
        ['CIN:', student['cin']],
        ['Sexe:', student['sexe']],
        ['Date de naissance:', student['date_naissance']],
        ['Nationalité:', student['nationalite']]
    ]
    
    # Academic Information
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Informations académiques", styles['Heading2']))
    academic_data = [
        ['Filière:', student.get('filiere_name', 'Non spécifiée')],
        ['Année universitaire:', student['annee_universitaire']],
        ['Chambre:', student['num_chambre'] if student['num_chambre'] not in [None, '', 'no room'] else 'Aucune'],
        ['Internat:', student['type_section']],
        ['Mobilité:', student['mobilite']],
        ['Vie associative:', student['vie_associative']],
        ['Bourse:', student['bourse']]
    ]
    
    # Create tables with improved styling
    table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ])
    
    # Add tables to elements
    elements.append(Table(personal_data, colWidths=[2*inch, 4*inch], style=table_style))
    elements.append(Spacer(1, 20))
    elements.append(Table(academic_data, colWidths=[2*inch, 4*inch], style=table_style))
    
    # Add footer with date and IAV information
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Paragraph(
        f"Institut Agronomique et Vétérinaire Hassan II - {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        footer_style
    ))
    
    # Build the PDF
    doc.build(elements)
    
    return pdf_path
