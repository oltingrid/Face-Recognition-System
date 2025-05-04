import sys

import face_recognition
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QLineEdit, QFileDialog, QLabel
)
from PySide6.QtCore import Qt
import mysql.connector
import cv2
import os
import json
import numpy as np


class AdminDashboard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard")
        self.setFixedSize(800, 600)


        self.db_connection = self.connect_to_db()


        self.initUI()


        self.load_table_data()

    def connect_to_db(self):
        """Connect to the MySQL database."""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="#Motroscuta19",
                database="face_recognition"
            )
            return connection
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not connect to the database:\n{e}")
            sys.exit()

    def initUI(self):
        """Initialize the Admin Dashboard UI."""
        self.layout = QVBoxLayout()


        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Image Path"])
        self.layout.addWidget(self.table)


        button_layout = QHBoxLayout()


        self.add_button = QPushButton("Add Person")
        self.add_button.setStyleSheet("background-color: green; color: white; font-size: 14px; padding: 5px;")
        self.add_button.clicked.connect(self.add_person_dialog)
        button_layout.addWidget(self.add_button)


        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setStyleSheet("background-color: red; color: white; font-size: 14px; padding: 5px;")
        self.remove_button.clicked.connect(self.remove_selected_person)
        button_layout.addWidget(self.remove_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def load_table_data(self):
        """Load the people table data from the database."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, name, image_path FROM people")
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            cursor.close()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading table data:\n{e}")

    def add_person_dialog(self):
        """Open a dialog to add a new person to the database."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Person")
        dialog.setFixedSize(400, 200)

        layout = QVBoxLayout()


        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name")
        layout.addWidget(name_input)


        choose_image_button = QPushButton("Choose Image")
        image_path_label = QLabel("No image selected.")
        layout.addWidget(image_path_label)

        def choose_image():
            file_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Images (*.jpg *.png)")
            if file_path:
                image_path_label.setText(file_path)

        choose_image_button.clicked.connect(choose_image)
        layout.addWidget(choose_image_button)


        save_button = QPushButton("Save")
        save_button.setStyleSheet("background-color: green; color: white;")
        save_button.clicked.connect(lambda: self.save_person(name_input.text(), image_path_label.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()

    def save_person(self, name, image_path, dialog):
        """Save a new person to the database."""
        if not name or not image_path or image_path == "No image selected.":
            QMessageBox.warning(self, "Input Error", "Please provide both name and image.")
            return

        try:

            image = cv2.imread(image_path)
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_encoding = face_recognition.face_encodings(rgb_img)[0]
            encoding_json = json.dumps(face_encoding.tolist())


            cursor = self.db_connection.cursor()
            query = "INSERT INTO people (name, face_encoding, image_path) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, encoding_json, image_path))
            self.db_connection.commit()

            QMessageBox.information(self, "Success", f"{name} has been added to the database.")
            dialog.accept()
            self.load_table_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving person:\n{e}")

    def remove_selected_person(self):
        """Remove the selected person from the database."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a person to remove.")
            return

        person_id = self.table.item(selected_row, 0).text()
        person_name = self.table.item(selected_row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove {person_name}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM people WHERE id = %s", (person_id,))
                self.db_connection.commit()

                QMessageBox.information(self, "Success", f"{person_name} has been removed from the database.")
                self.load_table_data()  # Refresh table
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Database Error", f"Error removing person:\n{e}")


if __name__ == "__main__":
    app = QApplication([])
    dashboard = AdminDashboard()
    dashboard.exec()
