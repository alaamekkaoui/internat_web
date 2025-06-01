from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLabel, QLineEdit, QDialog, QFormLayout, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from controllers.student_controller import StudentController

class StudentListView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student List')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.controller = StudentController()

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(500)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID', 'Matricule', 'Nom', 'Prénom', 'Filière', 'Internat', 'Chambre', 'Actions'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Action bar
        action_bar = QHBoxLayout()
        self.add_button = QPushButton('Ajouter')
        self.add_button.setIcon(QIcon('static/images/iav.png'))
        self.add_button.setStyleSheet('background: #145A32; color: white; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.add_button.clicked.connect(self.open_add_dialog)
        self.export_pdf_button = QPushButton('PDF')
        self.export_pdf_button.setIcon(QIcon.fromTheme('document-save'))
        self.export_pdf_button.setStyleSheet('background: #d32f2f; color: white; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.export_pdf_button.clicked.connect(self.export_pdf)
        self.export_xlsx_button = QPushButton('XLSX')
        self.export_xlsx_button.setIcon(QIcon.fromTheme('document-save-as'))
        self.export_xlsx_button.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.export_xlsx_button.clicked.connect(self.export_xlsx)
        self.import_button = QPushButton('Importer')
        self.import_button.setIcon(QIcon.fromTheme('document-open'))
        self.import_button.setStyleSheet('background: #0078d4; color: white; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.import_button.clicked.connect(self.import_xlsx)
        for btn in [self.add_button, self.export_pdf_button, self.export_xlsx_button, self.import_button]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumWidth(120)
            btn.setMinimumHeight(38)
            btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
            btn.setStyleSheet(btn.styleSheet() + 'QPushButton:pressed { color: #fff; background: #145A32; }')
            action_bar.addWidget(btn)
        self.layout.addLayout(action_bar)

        self.load_students()

    def load_students(self):
        students = self.controller.list_students()
        self.table.setRowCount(len(students))
        for row, student in enumerate(students):
            self.table.setItem(row, 0, QTableWidgetItem(str(student.get('id', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(student.get('matricule', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(student.get('nom', 'Aucun')))
            self.table.setItem(row, 3, QTableWidgetItem(student.get('prenom', 'Aucun')))
            self.table.setItem(row, 4, QTableWidgetItem(student.get('filiere_name', 'Aucun')))
            self.table.setItem(row, 5, QTableWidgetItem(student.get('type_section', 'Aucun')))
            self.table.setItem(row, 6, QTableWidgetItem(student.get('num_chambre', 'Aucun')))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #0078d4; color: white; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, s=student: self.show_details(s))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, s=student: self.open_edit_dialog(s))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #d32f2f; color: white; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, s=student: self.delete_student(s))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 7, actions_widget)

    def search(self, keyword):
        # Use get_filtered_students for search
        students = self.controller.get_filtered_students(keyword=keyword) if keyword else self.controller.list_students()
        self.table.setRowCount(len(students))
        for row, student in enumerate(students):
            self.table.setItem(row, 0, QTableWidgetItem(str(student.get('id', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(student.get('matricule', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(student.get('nom', 'Aucun')))
            self.table.setItem(row, 3, QTableWidgetItem(student.get('prenom', 'Aucun')))
            self.table.setItem(row, 4, QTableWidgetItem(student.get('filiere_name', 'Aucun')))
            self.table.setItem(row, 5, QTableWidgetItem(student.get('type_section', 'Aucun')))
            self.table.setItem(row, 6, QTableWidgetItem(student.get('num_chambre', 'Aucun')))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #fff; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, s=student: self.show_details(s))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #fff; color: #A7C636; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, s=student: self.open_edit_dialog(s))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #fff; color: #d32f2f; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, s=student: self.delete_student(s))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 7, actions_widget)

    def reset_search(self):
        self.search('')

    def show_details(self, student):
        # Modern details dialog with action buttons
        dialog = QDialog(self)
        dialog.setWindowTitle('Détails étudiant')
        layout = QVBoxLayout()
        info = QLabel()
        info.setTextFormat(Qt.RichText)
        info.setText(f"""
        <b>Matricule:</b> {student.get('matricule', 'Aucun')}<br>
        <b>Nom:</b> {student.get('nom', 'Aucun')}<br>
        <b>Prénom:</b> {student.get('prenom', 'Aucun')}<br>
        <b>Filière:</b> {student.get('filiere_name', 'Aucun')}<br>
        <b>Internat:</b> {student.get('type_section', 'Aucun')}<br>
        <b>Chambre:</b> {student.get('num_chambre', 'Aucun')}<br>
        <b>Pavillon:</b> {student.get('pavilion', 'Aucun')}<br>
        <b>Email:</b> {student.get('email', 'Aucun')}<br>
        <b>Téléphone:</b> {student.get('telephone', 'Aucun')}<br>
        <b>Date de naissance:</b> {student.get('date_naissance', 'Aucun')}<br>
        <b>CIN:</b> {student.get('cin', 'Aucun')}<br>
        <b>Nationalité:</b> {student.get('nationalite', 'Aucun')}<br>
        <b>Année universitaire:</b> {student.get('annee_universitaire', 'Aucun')}<br>
        <b>Bourse:</b> {student.get('bourse', 'Aucun')}<br>
        <b>Observation:</b> {student.get('observation', 'Aucun')}<br>
        """)
        info.setStyleSheet('font-size: 15px;')
        layout.addWidget(info)
        # Action bar
        action_bar = QHBoxLayout()
        btn_edit = QPushButton('Modifier')
        btn_edit.setIcon(QIcon.fromTheme('document-edit'))
        btn_edit.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 8px; font-weight: bold; min-width: 120px; min-height: 38px;')
        btn_edit.clicked.connect(lambda: (dialog.close(), self.open_edit_dialog(student)))
        btn_pdf = QPushButton('Exporter PDF')
        btn_pdf.setIcon(QIcon.fromTheme('document-save'))
        btn_pdf.setStyleSheet('background: #d32f2f; color: white; border-radius: 8px; font-weight: bold; min-width: 120px; min-height: 38px;')
        btn_pdf.clicked.connect(lambda: self.export_pdf())
        btn_xlsx = QPushButton('Exporter XLSX')
        btn_xlsx.setIcon(QIcon.fromTheme('document-save-as'))
        btn_xlsx.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 8px; font-weight: bold; min-width: 120px; min-height: 38px;')
        btn_xlsx.clicked.connect(lambda: self.export_xlsx())
        btn_import = QPushButton('Importer')
        btn_import.setIcon(QIcon.fromTheme('document-open'))
        btn_import.setStyleSheet('background: #0078d4; color: white; border-radius: 8px; font-weight: bold; min-width: 120px; min-height: 38px;')
        btn_import.clicked.connect(lambda: self.import_xlsx())
        for btn in [btn_edit, btn_pdf, btn_xlsx, btn_import]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
            btn.setStyleSheet(btn.styleSheet() + 'QPushButton:pressed { color: #fff; background: #145A32; }')
            action_bar.addWidget(btn)
        layout.addLayout(action_bar)
        dialog.setLayout(layout)
        dialog.exec_()

    def open_add_dialog(self):
        dialog = AddStudentDialog(self.controller, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_students()

    def open_edit_dialog(self, student):
        dialog = EditStudentDialog(self.controller, student, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_students()

    def delete_student(self, student):
        reply = QMessageBox.question(self, 'Supprimer', f"Supprimer l'étudiant {student.get('nom', 'Aucun')} ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_student(student.get('id'))
            self.load_students()

    def export_pdf(self):
        # TODO: Implement export PDF
        QMessageBox.information(self, 'Export PDF', 'Export PDF (à implémenter)')

    def export_xlsx(self):
        # TODO: Implement export XLSX
        QMessageBox.information(self, 'Export XLSX', 'Export XLSX (à implémenter)')

    def import_xlsx(self):
        # TODO: Implement import XLSX
        QMessageBox.information(self, 'Import', 'Import XLSX (à implémenter)')

class AddStudentDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Ajouter un étudiant')
        self.controller = controller
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.matricule_input = QLineEdit()
        self.layout.addRow('Nom:', self.nom_input)
        self.layout.addRow('Prénom:', self.prenom_input)
        self.layout.addRow('Matricule:', self.matricule_input)
        self.submit_button = QPushButton('Ajouter')
        self.submit_button.setStyleSheet('background: #145A32; color: white; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.submit_button.clicked.connect(self.add_student)
        self.layout.addWidget(self.submit_button)

    def add_student(self):
        data = {
            'nom': self.nom_input.text(),
            'prenom': self.prenom_input.text(),
            'matricule': self.matricule_input.text(),
        }
        result = self.controller.add_student(data)
        if 'error' in result:
            QMessageBox.critical(self, 'Erreur', result['error'])
        else:
            QMessageBox.information(self, 'Succès', 'Étudiant ajouté avec succès !')
            self.accept()

class EditStudentDialog(QDialog):
    def __init__(self, controller, student, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Modifier étudiant')
        self.controller = controller
        self.student = student
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.nom_input = QLineEdit(student.get('nom', ''))
        self.prenom_input = QLineEdit(student.get('prenom', ''))
        self.matricule_input = QLineEdit(student.get('matricule', ''))
        self.layout.addRow('Nom:', self.nom_input)
        self.layout.addRow('Prénom:', self.prenom_input)
        self.layout.addRow('Matricule:', self.matricule_input)
        self.submit_button = QPushButton('Enregistrer')
        self.submit_button.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.submit_button.clicked.connect(self.edit_student)
        self.layout.addWidget(self.submit_button)

    def edit_student(self):
        data = {
            'id': self.student.get('id'),
            'nom': self.nom_input.text(),
            'prenom': self.prenom_input.text(),
            'matricule': self.matricule_input.text(),
        }
        result = self.controller.edit_student(data)
        if 'error' in result:
            QMessageBox.critical(self, 'Erreur', result['error'])
        else:
            QMessageBox.information(self, 'Succès', 'Étudiant modifié avec succès !')
            self.accept()
