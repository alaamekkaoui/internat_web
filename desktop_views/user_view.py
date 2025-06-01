# This file will contain the PyQt5 translation of the user_route logic
# Example: List users and add a new user
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLabel, QLineEdit, QDialog, QFormLayout, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from controllers.user_controller import UserController

class UserListView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Utilisateurs')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.controller = UserController()

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(500)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Nom d’utilisateur', 'Rôle', 'Email', 'Actions'])
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

        self.load_users()

    def load_users(self):
        users = self.controller.list_users()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.get('id', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(user.get('username', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(user.get('role', 'Aucun')))
            self.table.setItem(row, 3, QTableWidgetItem(user.get('email', 'Aucun')))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #0078d4; color: white; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, u=user: self.show_details(u))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, u=user: self.open_edit_dialog(u))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #d32f2f; color: white; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, u=user: self.delete_user(u))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def search(self, keyword):
        users = self.controller.list_users()
        if keyword:
            keyword_lower = keyword.lower()
            users = [u for u in users if keyword_lower in str(u.get('username', '')).lower() or keyword_lower in str(u.get('role', '')).lower() or keyword_lower in str(u.get('email', '')).lower()]
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.get('id', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(user.get('username', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(user.get('role', 'Aucun')))
            self.table.setItem(row, 3, QTableWidgetItem(user.get('email', 'Aucun')))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #fff; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, u=user: self.show_details(u))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #fff; color: #A7C636; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, u=user: self.open_edit_dialog(u))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #fff; color: #d32f2f; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, u=user: self.delete_user(u))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def reset_search(self):
        self.search('')

    def show_details(self, user):
        dialog = QDialog(self)
        dialog.setWindowTitle('Détails utilisateur')
        layout = QVBoxLayout()
        info = QLabel()
        info.setTextFormat(Qt.RichText)
        info.setText(f"""
        <b>Nom d’utilisateur:</b> {user.get('username', 'Aucun')}<br>
        <b>Rôle:</b> {user.get('role', 'Aucun')}<br>
        <b>Email:</b> {user.get('email', 'Aucun')}<br>
        <b>Date de création:</b> {user.get('created_at', 'Aucun')}<br>
        """)
        info.setStyleSheet('font-size: 15px;')
        layout.addWidget(info)
        # Action bar
        action_bar = QHBoxLayout()
        btn_edit = QPushButton('Modifier')
        btn_edit.setIcon(QIcon.fromTheme('document-edit'))
        btn_edit.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 8px; font-weight: bold; min-width: 120px; min-height: 38px;')
        btn_edit.clicked.connect(lambda: (dialog.close(), self.open_edit_dialog(user)))
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
        dialog = AddUserDialog(self.controller, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

    def open_edit_dialog(self, user):
        dialog = EditUserDialog(self.controller, user, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

    def delete_user(self, user):
        reply = QMessageBox.question(self, 'Supprimer', f"Supprimer l’utilisateur {user.get('username', 'Aucun')} ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_user(user.get('id'))
            self.load_users()

    def export_pdf(self):
        QMessageBox.information(self, 'Export PDF', 'Export PDF (à implémenter)')

    def export_xlsx(self):
        QMessageBox.information(self, 'Export XLSX', 'Export XLSX (à implémenter)')

    def import_xlsx(self):
        QMessageBox.information(self, 'Import', 'Import XLSX (à implémenter)')

class AddUserDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Ajouter un utilisateur')
        self.controller = controller
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.role_input = QLineEdit()
        self.email_input = QLineEdit()
        self.layout.addRow('Nom d’utilisateur:', self.username_input)
        self.layout.addRow('Mot de passe:', self.password_input)
        self.layout.addRow('Rôle:', self.role_input)
        self.layout.addRow('Email:', self.email_input)
        self.submit_button = QPushButton('Ajouter')
        self.submit_button.setStyleSheet('background: #145A32; color: white; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.submit_button.clicked.connect(self.add_user)
        self.layout.addWidget(self.submit_button)

    def add_user(self):
        data = {
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'role': self.role_input.text(),
            'email': self.email_input.text(),
        }
        result = self.controller.add_user(data)
        if 'error' in result:
            QMessageBox.critical(self, 'Erreur', result['error'])
        else:
            QMessageBox.information(self, 'Succès', 'Utilisateur ajouté avec succès !')
            self.accept()

class EditUserDialog(QDialog):
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Modifier utilisateur')
        self.controller = controller
        self.user = user
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.username_input = QLineEdit(user.get('username', ''))
        self.password_input = QLineEdit()
        self.role_input = QLineEdit(user.get('role', ''))
        self.email_input = QLineEdit(user.get('email', ''))
        self.layout.addRow('Nom d’utilisateur:', self.username_input)
        self.layout.addRow('Mot de passe:', self.password_input)
        self.layout.addRow('Rôle:', self.role_input)
        self.layout.addRow('Email:', self.email_input)
        self.submit_button = QPushButton('Enregistrer')
        self.submit_button.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 8px; font-weight: bold; min-height: 38px;')
        self.submit_button.clicked.connect(self.edit_user)
        self.layout.addWidget(self.submit_button)

    def edit_user(self):
        data = {
            'id': self.user.get('id'),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'role': self.role_input.text(),
            'email': self.email_input.text(),
        }
        result = self.controller.edit_user(data)
        if 'error' in result:
            QMessageBox.critical(self, 'Erreur', result['error'])
        else:
            QMessageBox.information(self, 'Succès', 'Utilisateur modifié avec succès !')
            self.accept()
