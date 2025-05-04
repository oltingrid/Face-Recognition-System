import sys
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QStatusBar, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from src.simple_facerec import SimpleFacerec
import admin_login
from admin_login import AdminLogin
from admin_dashboard import AdminDashboard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Face Recognition Access System")
        self.setGeometry(100, 100, 900, 700)

        self.sfr = SimpleFacerec()
        self.sfr.load_encoding_from_db()


        self.cap = cv2.VideoCapture(0)


        self.initUI()


        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

    def initUI(self):

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()


        self.video_label = QLabel()
        self.video_label.setStyleSheet("border: 1px solid black;")
        self.main_layout.addWidget(self.video_label)


        self.status_panel_layout = QHBoxLayout()


        self.status_label = QLabel("Status: Waiting for recognition...")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: lightgray;")
        self.status_panel_layout.addWidget(self.status_label)


        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: red; color: white; font-size: 12px; padding: 5px;")
        self.exit_button.setMinimumSize(120, 50) # Smaller button width
        self.exit_button.clicked.connect(self.close_application)
        self.status_panel_layout.addWidget(self.exit_button, alignment=Qt.AlignRight)

        self.main_layout.addLayout(self.status_panel_layout)


        admin_button = QPushButton("Admin Login")
        admin_button.setStyleSheet("background-color: blue; color: white; font-size: 14px; padding: 5px;")
        admin_button.setMinimumSize(120, 50)
        admin_button.clicked.connect(self.open_admin_login)
        self.status_panel_layout.addWidget(admin_button)


        self.central_widget.setLayout(self.main_layout)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.status_label.setText("Error: Unable to access the camera!")
            self.status_label.setStyleSheet("background-color: red; color: white; font-size: 14px;")
            return


        face_locations, face_names = self.sfr.detect_known_faces(frame)


        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]


            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                frame, name, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )


        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)


        self.video_label.setPixmap(QPixmap.fromImage(q_image))


        num_faces = len(face_names)
        if num_faces > 1:
            self.status_label.setText(f"Multiple Faces Detected: {num_faces} people. Try again")
            self.status_label.setStyleSheet("background-color: orange; color: black; font-size: 14px; padding: 10px;")
        elif num_faces == 1:
            if "Unknown" in face_names:
                self.status_label.setText("Access Denied: Unknown face detected")
                self.status_label.setStyleSheet("background-color: red; color: white; font-size: 14px; padding: 10px;")
            else:
                recognized_names = [name for name in face_names if name != "Unknown"]
                self.status_label.setText(f"Access Granted: {', '.join(recognized_names)}")
                self.status_label.setStyleSheet(
                    "background-color: green; color: white; font-size: 14px; padding: 10px;")
        else:
            self.status_label.setText("No faces detected")
            self.status_label.setStyleSheet("background-color: gray; color: white; font-size: 14px; padding: 10px;")

    def open_admin_login(self):
        """Open the Admin Login Dialog."""
        dialog = AdminLogin(self)
        if dialog.exec():
            QMessageBox.information(self, "Admin Access", "Welcome to the Admin Dashboard!")


            admin_dashboard = AdminDashboard(self)
            admin_dashboard.exec()
        else:
            QMessageBox.information(self, "Admin Access", "Admin login canceled.")

    def close_application(self):

        self.cap.release()
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
