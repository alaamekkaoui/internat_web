from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation
from controllers.user_controller import UserController
import os

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login - Internat Desktop App')
        self.setFixedSize(520, 480)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self.controller = UserController()
        self.init_ui()
        self.fade_in()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(18)

        # Logo
        logo_path = os.path.join('static', 'images', 'iav.png')
        if os.path.exists(logo_path):
            logo = QLabel()
            pixmap = QPixmap(logo_path)
            logo.setPixmap(pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)

        # Title
        title = QLabel('INTERNAT IAV HASSAN II')
        title.setFont(QFont('Segoe UI', 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('color: #0078d4; letter-spacing: 2px; margin-bottom: 10px;')
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel('Sign in to continue')
        subtitle.setFont(QFont('Segoe UI', 13))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('color: #555; margin-bottom: 18px;')
        layout.addWidget(subtitle)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setMinimumHeight(38)
        self.username_input.setFont(QFont('Segoe UI', 12))
        self.username_input.setStyleSheet('padding-left: 12px;')
        layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(38)
        self.password_input.setFont(QFont('Segoe UI', 12))
        self.password_input.setStyleSheet('padding-left: 12px;')
        layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.setMinimumHeight(40)
        self.login_button.setFont(QFont('Segoe UI', 13, QFont.Bold))
        self.login_button.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d4, stop:1 #00b4d8); border-radius: 10px;')
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Footer
        footer = QLabel('© 2025 IAV Hassan II. All rights reserved.')
        footer.setFont(QFont('Segoe UI', 9))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet('color: #888; margin-top: 20px;')
        layout.addWidget(footer)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        success, user, message = self.controller.login_user(username, password)
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, 'Login Failed', message or 'Invalid username or password.')

    def fade_in(self):
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()
