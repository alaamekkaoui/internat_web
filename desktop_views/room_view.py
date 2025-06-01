# This file will contain the PyQt5 translation of the room_route logic
# Example: List rooms and add a new room
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QHBoxLayout, QDialog, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from controllers.room_controller import RoomController

class RoomListView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Room List')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.controller = RoomController()

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(500)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Numéro', 'Pavillon', 'Type', 'Capacité', 'Occupée', 'Actions'])
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

        self.load_rooms()

    def load_rooms(self):
        rooms = self.controller.list_rooms()
        self.table.setRowCount(len(rooms))
        for row, room in enumerate(rooms):
            self.table.setItem(row, 0, QTableWidgetItem(str(room.get('id', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(room.get('room_number', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(room.get('pavilion', 'Aucun')))
            self.table.setItem(row, 3, QTableWidgetItem(room.get('room_type', 'Aucun')))
            self.table.setItem(row, 4, QTableWidgetItem(str(room.get('capacity', 'Aucun'))))
            self.table.setItem(row, 5, QTableWidgetItem('Oui' if room.get('is_used') else 'Non'))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #0078d4; color: white; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, r=room: self.show_details(r))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #A7C636; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, r=room: self.open_edit_dialog(r))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #d32f2f; color: white; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, r=room: self.delete_room(r))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 6, actions_widget)

    def search(self, keyword):
        # No get_filtered_rooms in controller, so filter here
        rooms = self.controller.list_rooms()
        if keyword:
            keyword_lower = keyword.lower()
            rooms = [r for r in rooms if keyword_lower in str(r.get('room_number', '')).lower() or keyword_lower in str(r.get('pavilion', '')).lower() or keyword_lower in str(r.get('room_type', '')).lower()]
        self.table.setRowCount(len(rooms))
        for row, room in enumerate(rooms):
            self.table.setItem(row, 0, QTableWidgetItem(str(room.get('room_number', 'Aucun'))))
            self.table.setItem(row, 1, QTableWidgetItem(room.get('pavilion', 'Aucun')))
            self.table.setItem(row, 2, QTableWidgetItem(room.get('room_type', 'Aucun')))
            self.table.setItem(row, 3, QTableWidgetItem(str(room.get('capacity', 'Aucun'))))
            self.table.setItem(row, 4, QTableWidgetItem(str(room.get('used_capacity', 'Aucun'))))
            # Actions
            actions_layout = QHBoxLayout()
            btn_detail = QPushButton()
            btn_detail.setIcon(QIcon.fromTheme('document-preview'))
            btn_detail.setToolTip('Détails')
            btn_detail.setStyleSheet('background: #fff; color: #145A32; border-radius: 6px; min-width: 36px;')
            btn_detail.clicked.connect(lambda _, r=room: self.show_details(r))
            btn_edit = QPushButton()
            btn_edit.setIcon(QIcon.fromTheme('document-edit'))
            btn_edit.setToolTip('Modifier')
            btn_edit.setStyleSheet('background: #fff; color: #A7C636; border-radius: 6px; min-width: 36px;')
            btn_edit.clicked.connect(lambda _, r=room: self.open_edit_dialog(r))
            btn_delete = QPushButton()
            btn_delete.setIcon(QIcon.fromTheme('edit-delete'))
            btn_delete.setToolTip('Supprimer')
            btn_delete.setStyleSheet('background: #fff; color: #d32f2f; border-radius: 6px; min-width: 36px;')
            btn_delete.clicked.connect(lambda _, r=room: self.delete_room(r))
            actions_widget = QWidget()
            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 5, actions_widget)

    def reset_search(self):
        self.search('')

    def show_details(self, room):
        msg = f"""
        <b>Numéro:</b> {room.get('room_number', 'Aucun')}<br>
        <b>Pavillon:</b> {room.get('pavilion', 'Aucun')}<br>
        <b>Type:</b> {room.get('room_type', 'Aucun')}<br>
        <b>Capacité:</b> {room.get('capacity', 'Aucun')}<br>
        <b>Occupée:</b> {'Oui' if room.get('is_used') else 'Non'}<br>
        """
        detail_box = QMessageBox(self)
        detail_box.setWindowTitle('Détails chambre')
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
        # TODO: Implement add room dialog
        QMessageBox.information(self, 'Ajouter', 'Ajouter une chambre (à implémenter)')

    def open_edit_dialog(self, room):
        # TODO: Implement edit room dialog
        QMessageBox.information(self, 'Modifier', f"Modifier la chambre {room.get('room_number', 'Aucun')} (à implémenter)")

    def delete_room(self, room):
        reply = QMessageBox.question(self, 'Supprimer', f"Supprimer la chambre {room.get('room_number', 'Aucun')} ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_room(room.get('id'))
            self.load_rooms()
    def export_pdf(self):
        # TODO: Implement export PDF
        QMessageBox.information(self, 'Export PDF', 'Export PDF (à implémenter)')
    def export_xlsx(self):
        # TODO: Implement export XLSX
        QMessageBox.information(self, 'Export XLSX', 'Export XLSX (à implémenter)')
    def import_xlsx(self):
        # TODO: Implement import XLSX
        QMessageBox.information(self, 'Import', 'Import XLSX (à implémenter)')
