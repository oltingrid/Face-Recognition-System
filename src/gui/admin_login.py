import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt


class AdminLogin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Admin Login")
        self.setFixedSize(400, 200)


        self.initUI()


        self.admin_username = "admin"
        self.admin_password = "password123"

    def initUI(self):

        main_layout = QVBoxLayout()

        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)


        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)  # Mask password input
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)


        buttons_layout = QHBoxLayout()
        login_button = QPushButton("Login")
        login_button.setStyleSheet("background-color: green; color: white; padding: 5px; font-size: 14px;")
        login_button.clicked.connect(self.handle_login)
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: red; color: white; padding: 5px; font-size: 14px;")
        cancel_button.clicked.connect(self.reject)  # Close the dialog

        buttons_layout.addWidget(login_button)
        buttons_layout.addWidget(cancel_button)


        main_layout.addLayout(username_layout)
        main_layout.addLayout(password_layout)
        main_layout.addLayout(buttons_layout)


        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Check credentials
        if username == self.admin_username and password == self.admin_password:
            QMessageBox.information(self, "Login Successful", "Welcome, Admin!")
            self.accept()  # Close the dialog and return success
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminLogin()
    if window.exec():
        print("Login Successful: Admin Access Granted")
    else:
        print("Login Failed or Canceled")
    sys.exit(app.exec())
