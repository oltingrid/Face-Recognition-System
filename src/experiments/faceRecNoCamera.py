import face_recognition
import cv2
import numpy as np

# Load known images and create encodings
known_face_encodings = []
known_face_names = []

famous_people = {
    "famous_people/angelina_jolie.jpg": "Angelina Jolie",
    "famous_people/sofia_vergara.jpg": "Sofia Vergara",
}

for image_path, name in famous_people.items():
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    known_face_names.append(name)

# Open the webcam
video_capture = cv2.VideoCapture(0)
print("Starting live camera. Press 'q' to exit.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame. Exiting...")
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Detect face locations
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = []

    if face_locations:
        # Compute encodings only if faces are detected
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Loop through detected faces
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    cv2.imshow('Live Camera - Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
