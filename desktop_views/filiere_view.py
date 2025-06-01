# This file will contain the PyQt5 translation of the filiere_route logic
# Example: List filieres and add a new filiere
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLabel, QLineEdit, QDialog, QFormLayout, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from controllers.filiere_controller import FiliereController

class FiliereListView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Filiere List')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.controller = FiliereController()

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(500)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Nom', 'Créée le', 'Actions'])
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

        self.load_filieres()

    def load_filieres(self):
        filieres = self.controller.list_filieres()
        self.table.setRowCount(len(filieres))
        for row, filiere in enumerate(filieres):
            self.table.setItem(row, 0, QTableWidgetItem(str(filiere.get('id', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(filiere.get('name', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(str(filiere.get('created_at', 'Aucun'))))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #0078d4; color: white; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, f=filiere: self.show_details(f))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, f=filiere: self.open_edit_dialog(f))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #d32f2f; color: white; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, f=filiere: self.delete_filiere(f))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 3, actions_widget)

    def search(self, keyword):
        filieres = self.controller.list_filieres()
        if keyword:
            keyword_lower = keyword.lower()
            filieres = [f for f in filieres if keyword_lower in str(f.get('name', '')).lower() or keyword_lower in str(f.get('responsable', '')).lower() or keyword_lower in str(f.get('email', '')).lower()]
        self.table.setRowCount(len(filieres))
        for row, filiere in enumerate(filieres):
            self.table.setItem(row, 0, QTableWidgetItem(str(filiere.get('id', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(filiere.get('name', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(filiere.get('responsable', 'Aucun')))
            self.table.setItem(row, 3, QTableWidgetItem(filiere.get('email', 'Aucun')))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #fff; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, f=filiere: self.show_details(f))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #fff; color: #A7C636; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, f=filiere: self.open_edit_dialog(f))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #fff; color: #d32f2f; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, f=filiere: self.delete_filiere(f))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def reset_search(self):
        self.search('')

    def show_details(self, filiere):
        msg = f"""
        <b>Nom:</b> {filiere.get('name', 'Aucun')}<br>
        <b>Créée le:</b> {filiere.get('created_at', 'Aucun')}<br>
        """
        detail_box = QMessageBox(self)
        detail_box.setWindowTitle('Détails filière')
        detail_box.setTextFormat(Qt.RichText)
        detail_box.setText(msg)
        detail_box.addButton('Modifier', QMessageBox.ActionRole)
        detail_box.addButton('Exporter PDF', QMessageBox.ActionRole)
        detail_box.addButton('Exporter XLSX', QMessageBox.ActionRole)
        detail_box.addButton('Importer', QMessageBox.ActionRole)
        detail_box.addButton(QMessageBox.Close)
        ret = detail_box.exec_()
        # TODO: Connect actions to real logic

    def open_add_dialog(self):
        # TODO: Implement add filiere dialog
        QMessageBox.information(self, 'Ajouter', 'Ajouter une filière (à implémenter)')

    def open_edit_dialog(self, filiere):
        # TODO: Implement edit filiere dialog
        QMessageBox.information(self, 'Modifier', f"Modifier la filière {filiere.get('name', 'Aucun')} (à implémenter)")

    def delete_filiere(self, filiere):
        reply = QMessageBox.question(self, 'Supprimer', f"Supprimer la filière {filiere.get('name', 'Aucun')} ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_filiere(filiere.get('id'))
            self.load_filieres()
    def export_pdf(self):
        # TODO: Implement export PDF
        QMessageBox.information(self, 'Export PDF', 'Export PDF (à implémenter)')
    def export_xlsx(self):
        # TODO: Implement export XLSX
        QMessageBox.information(self, 'Export XLSX', 'Export XLSX (à implémenter)')
    def import_xlsx(self):
        # TODO: Implement import XLSX
        QMessageBox.information(self, 'Import', 'Import XLSX (à implémenter)')
