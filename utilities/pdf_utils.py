# utilities/pdf_utils.py
import os
from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

def export_pdf(data, pdf_path):
    """Generate a PDF file with student data and IAV logo."""
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Create styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )

        # Create the content
        content = []

        # Add IAV logo at the top
        logo_path = os.path.join(os.path.dirname(__file__), '../static/images/iav.png')
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.5*inch, height=1.5*inch)
            img.hAlign = 'CENTER'
            content.append(img)
            content.append(Spacer(1, 12))

        # Add title
        content.append(Paragraph("Liste des Étudiants", title_style))
        content.append(Spacer(1, 20))

        # Add generation date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray
        )
        content.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
        content.append(Spacer(1, 20))

        # Prepare table data
        table_data = [['Matricule', 'Nom', 'Prénom', 'Filière', 'Chambre']]
        for student in data:
            table_data.append([
                student['matricule'],
                student['nom'],
                student['prenom'],
                student.get('filiere_name', ''),
                student.get('num_chambre', '')
            ])

        # Create table
        table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 2*inch, 1*inch])
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

        # Build the PDF
        doc.build(content)
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

def save_pdf(pdf_folder, filename, pdf_stream):
    """Save a PDF stream to a file."""
    pdf_path = os.path.join(pdf_folder, filename)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_stream.read())
    return pdf_path
