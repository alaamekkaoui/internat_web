from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QSizePolicy, QLineEdit, QSpacerItem
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QFile
from desktop_views.student_view import StudentListView
from desktop_views.room_view import RoomListView
from desktop_views.filiere_view import FiliereListView
from desktop_views.user_view import UserListView
from desktop_views.login_dialog import LoginDialog
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Internat Desktop App')
        self.setMinimumSize(1100, 700)
        # IAV Hassan II color palette
        iav_primary = '#145A32'  # dark green
        iav_secondary = '#A7C636'  # light green
        iav_accent = '#0078d4'  # blue for action
        self.setStyleSheet(self.styleSheet() + f"background: #f5f7fa;")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Sidebar
        self.sidebar = QVBoxLayout()
        self.sidebar.setContentsMargins(0, 0, 0, 0)
        self.sidebar.setSpacing(18)
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(self.sidebar)
        self.sidebar_widget.setFixedWidth(220)
        self.sidebar_widget.setStyleSheet(f'background: #fff; border-right: 1px solid #e0e0e0;')

        # Logo
        logo_path = os.path.join('static', 'images', 'iav.png')
        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        self.sidebar.addWidget(logo_label)

        # App name
        app_name = QLabel('INTERNAT IAV')
        app_name.setFont(QFont('Segoe UI', 15, QFont.Bold))
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet(f'color: {iav_primary}; letter-spacing: 1px;')
        self.sidebar.addWidget(app_name)

        # Search bar (global, filters current view)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Rechercher...')
        self.search_input.setMinimumHeight(36)
        self.search_input.setFont(QFont('Segoe UI', 11))
        self.search_input.setStyleSheet(f'border: 1px solid {iav_secondary}; border-radius: 8px; padding-left: 12px; margin: 0 18px; background: #f8fff4;')
        self.sidebar.addWidget(self.search_input)
        self.search_input.returnPressed.connect(self.handle_search)

        # Add reset button next to search bar
        self.reset_button = QPushButton('Réinitialiser')
        self.reset_button.setMinimumHeight(36)
        self.reset_button.setFont(QFont('Segoe UI', 11))
        self.reset_button.setStyleSheet('background: #fff; color: #145A32; border: 1px solid #A7C636; border-radius: 8px; margin: 0 18px;')
        self.reset_button.clicked.connect(self.handle_reset_search)
        search_bar_layout = QHBoxLayout()
        search_bar_layout.addWidget(self.search_input)
        search_bar_layout.addWidget(self.reset_button)
        search_bar_widget = QWidget()
        search_bar_widget.setLayout(search_bar_layout)
        self.sidebar.insertWidget(3, search_bar_widget)
        self.sidebar.removeWidget(self.search_input)

        # Sidebar buttons
        self.btn_students = QPushButton('Étudiants')
        self.btn_rooms = QPushButton('Chambres')
        self.btn_filieres = QPushButton('Filières')
        self.btn_users = QPushButton('Utilisateurs')
        for btn in [self.btn_students, self.btn_rooms, self.btn_filieres, self.btn_users]:
            btn.setMinimumHeight(44)
            btn.setFont(QFont('Segoe UI', 12, QFont.Bold))
            btn.setStyleSheet(f'QPushButton {{background: #f5f7fa; border-radius: 8px; margin: 6px 18px; color: {iav_primary};}} QPushButton:hover {{background: {iav_secondary}; color: #fff;}}')
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.sidebar.addWidget(btn)
        self.sidebar.addStretch(1)

        # Main content area
        self.stack = QStackedWidget()
        self.student_view = StudentListView()
        self.room_view = RoomListView()
        self.filiere_view = FiliereListView()
        self.user_view = UserListView()
        self.stack.addWidget(self.student_view)
        self.stack.addWidget(self.room_view)
        self.stack.addWidget(self.filiere_view)
        self.stack.addWidget(self.user_view)

        # Connect buttons
        self.btn_students.clicked.connect(lambda: self.switch_view(self.student_view))
        self.btn_rooms.clicked.connect(lambda: self.switch_view(self.room_view))
        self.btn_filieres.clicked.connect(lambda: self.switch_view(self.filiere_view))
        self.btn_users.clicked.connect(lambda: self.switch_view(self.user_view))

        # Default view
        self.stack.setCurrentWidget(self.student_view)
        self.current_view = self.student_view

        # Add sidebar and main area to layout
        self.layout.addWidget(self.sidebar_widget)
        self.layout.addWidget(self.stack)
        self.layout.setStretch(0, 0)
        self.layout.setStretch(1, 1)

    def switch_view(self, view):
        self.stack.setCurrentWidget(view)
        self.current_view = view
        self.search_input.clear()

    def handle_search(self):
        keyword = self.search_input.text().strip()
        # Each view must implement a 'search' method
        if hasattr(self.current_view, 'search'):
            self.current_view.search(keyword)

    def handle_reset_search(self):
        if hasattr(self.current_view, 'reset_search'):
            self.current_view.reset_search()
        self.search_input.clear()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    # Load QSS stylesheet
    qss_file = QFile('desktop_views/style.qss')
    if qss_file.open(QFile.ReadOnly | QFile.Text):
        app.setStyleSheet(str(qss_file.readAll(), encoding='utf-8'))
    # Show login dialog first
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
