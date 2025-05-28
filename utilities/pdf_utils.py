# utilities/pdf_utils.py
import io
import os
from flask import send_file
from datetime import datetime
import tempfile
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# Font and image paths
AMIRI_FONT_PATH = os.path.join(os.path.dirname(__file__), '../static/font/Amiri-Regular.ttf')
LOGO_PATH = os.path.join(os.path.dirname(__file__), '../static/images/iav.png')

# Arabic RTL helper
def shape_arabic(text):
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text

class CustomPDF(FPDF):
    def header(self):
        logo_h = 22
        logo_w = 22
        logo_y = 12
        center_x = self.w / 2
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=center_x - logo_w / 2, y=logo_y, w=logo_w, h=logo_h)

        left_x = 10
        right_x = center_x + logo_w / 2 + 4
        logo_left = center_x - logo_w / 2 - 4
        text_y = logo_y + 1
        text_h = 8

        if os.path.exists(AMIRI_FONT_PATH):
            if 'Amiri' not in self.fonts:
                self.add_font('Amiri', '', AMIRI_FONT_PATH, uni=True)
            self.set_font('Amiri', '', 14)
        else:
            self.set_font('Helvetica', 'B', 13)

        # French text (2 lines on the left)
        self.set_xy(left_x, text_y)
        self.multi_cell(logo_left - left_x, text_h, 
            "Institut Agronomique et Vétérinaire\nHassan II", align='L')

        # Arabic (right)
        self.set_xy(right_x, text_y + 2)  # Slight vertical adjustment
        arabic_text = shape_arabic('معهد الحسن الثاني للزراعة والبيطرة')
        self.cell(self.w - right_x - 10, text_h * 2, arabic_text, ln=0, align='R')

        self.ln(logo_h + 8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        year = datetime.now().year
        footer_text = f"Copyright © {year} IAV HASSAN II. Tous les droits réservés. Mentions légales"
        self.cell(0, 10, footer_text, 0, 0, 'C')

def export_pdf(data):
    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    if os.path.exists(AMIRI_FONT_PATH):
        pdf.add_font('Amiri', '', AMIRI_FONT_PATH, uni=True)
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 12, 'Liste des Étudiants', ln=1, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1, align='C')
    pdf.ln(5)

    headers = ['Matricule', 'Nom Complet', 'Type Internat', 'Année universitaire', 'Chambre']
    col_widths = [30, 50, 35, 40, 25]
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font('Helvetica', 'B', 11)

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font('Helvetica', '', 10)
    pdf.set_fill_color(245, 245, 245)
    fill = False
    for student in data:
        nom_complet = f"{student.get('nom', '')} {student.get('prenom', '')}"
        type_section = student.get('type_section', '') or 'Non spécifié'
        annee = student.get('annee_universitaire', '') or 'Non spécifiée'
        chambre = student.get('num_chambre') if student.get('num_chambre') not in [None, '', 'no room'] else 'Aucune'
        row = [
            str(student.get('matricule', '')),
            nom_complet,
            type_section,
            annee,
            str(chambre)
        ]
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], 9, val, border=1, align='C', fill=fill)
        pdf.ln()
        fill = not fill

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

def save_pdf(pdf_folder, filename, pdf_stream):
    path = os.path.join(pdf_folder, filename)
    with open(path, 'wb') as f:
        f.write(pdf_stream.read())
    return path

def generate_student_pdf(student):
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, f"student_profile_{student['id']}.pdf")
    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    if os.path.exists(AMIRI_FONT_PATH):
        pdf.add_font('Amiri', '', AMIRI_FONT_PATH, uni=True)
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 12, "Profil de l'étudiant", ln=1, align='C')
    pdf.ln(5)

    if student.get('photo'):
        photo_path = os.path.join('static', 'uploads', student['photo'])
        if os.path.exists(photo_path):
            pdf.image(photo_path, x=(pdf.w - 40) / 2, w=40, h=40)
            pdf.ln(25)

    pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(0, 10, f"{student['prenom']} {student['nom']}", ln=1, align='C')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f"Matricule: {student['matricule']}", ln=1, align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, "Informations personnelles", ln=1)
    pdf.set_font('Helvetica', '', 11)
    personal = [
        ('Nom:', student['nom']),
        ('Prénom:', student['prenom']),
        ('CIN:', student['cin']),
        ('Sexe:', student['sexe']),
        ('Date de naissance:', student['date_naissance']),
        ('Nationalité:', student['nationalite']),
    ]
    for label, value in personal:
        pdf.cell(45, 8, label, border=0)
        pdf.cell(0, 8, str(value), border=0, ln=1)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, "Informations académiques", ln=1)
    pdf.set_font('Helvetica', '', 11)
    academic = [
        ('Filière:', student.get('filiere_name', 'Non spécifiée')),
        ('Année universitaire:', student['annee_universitaire']),
        ('Chambre:', student['num_chambre'] if student['num_chambre'] not in [None, '', 'no room'] else 'Aucune'),
        ('Internat:', student['type_section']),
        ('Mobilité:', student['mobilite']),
        ('Vie associative:', student['vie_associative']),
        ('Bourse:', student['bourse']),
    ]
    for label, value in academic:
        pdf.cell(45, 8, label, border=0)
        pdf.cell(0, 8, str(value), border=0, ln=1)

    pdf.output(path)
    return path
