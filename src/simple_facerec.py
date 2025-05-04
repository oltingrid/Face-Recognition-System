import face_recognition
import cv2
import os
import glob
import numpy as np
import mysql.connector
import json

class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.25

    def connect_to_db(self):
        """Connect to the MySQL database."""
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="#Motroscuta19",
            database="face_recognition"
        )
        return connection

    def load_encoding_images(self, images_path):
        """
        Load encoding images from a folder (legacy method).
        Use this to bulk load images from a directory.
        """
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        print(f"{len(images_path)} encoding images found.")

        for img_path in images_path:
            img = cv2.imread(img_path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            basename = os.path.basename(img_path)
            (filename, ext) = os.path.splitext(basename)

            img_encoding = face_recognition.face_encodings(rgb_img)[0]
            self.known_face_encodings.append(img_encoding)
            self.known_face_names.append(filename)


            self.save_encoding_to_db(filename, img_encoding, img_path)

        print("Encoding images loaded and saved to the database.")

    def load_encoding_from_db(self):
        """
        Load face encodings and names from the database.
        """
        try:
            connection = self.connect_to_db()
            cursor = connection.cursor()

            cursor.execute("SELECT name, face_encoding FROM people")
            rows = cursor.fetchall()

            for row in rows:
                name = row[0]
                encoding = json.loads(row[1])
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)

            print(f"Loaded {len(self.known_face_encodings)} faces from the database.")

            cursor.close()
            connection.close()
        except mysql.connector.Error as e:
            print(f"Error loading data from database: {e}")

    def save_encoding_to_db(self, name, encoding, image_path=None):
        """
        Save a face encoding, name, and optional image path to the database.
        """
        try:
            encoding_json = json.dumps(encoding.tolist())  # Serialize encoding
            connection = self.connect_to_db()
            cursor = connection.cursor()

            query = "INSERT INTO people (name, face_encoding, image_path) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, encoding_json, image_path))
            connection.commit()

            print(f"Saved {name} to the database.")

            cursor.close()
            connection.close()
        except mysql.connector.Error as e:
            print(f"Error saving to database: {e}")

    def detect_known_faces(self, frame):
        """
        Detect and recognize known faces in a frame.
        """
        if frame is None or frame.size == 0:
            print("Invalid frame received. Skipping detection...")
            return [], []

        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            if any(matches):
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            face_names.append(name)

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names

    def add_person_dynamically(self, name, frame, image_path=None):
        """
        Dynamically add a new person's face to the database.
        :param name: Name of the person
        :param frame: Video frame or image containing the person's face
        :param image_path: Optional path to the image file
        """
        try:
            small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_encodings = face_recognition.face_encodings(rgb_frame)

            if len(face_encodings) == 0:
                print("No face detected in the frame. Please try again.")
                return

            face_encoding = face_encodings[0]

            self.save_encoding_to_db(name, face_encoding, image_path)
            print(f"Successfully added {name} to the database.")

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(name)

        except Exception as e:
            print(f"Error adding person dynamically: {e}")

