import cv2
from simple_facerec import SimpleFacerec


sfr = SimpleFacerec()


sfr.load_encoding_from_db()


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()


    face_locations, face_names = sfr.detect_known_faces(frame)


    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]


        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)


    cv2.imshow("Frame", frame)


    key = cv2.waitKey(1)

    if key == ord('a'):
        print("Enter the name of the person: ")
        person_name = input("Name: ")
        sfr.add_person_dynamically(person_name, frame)

    if key == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
