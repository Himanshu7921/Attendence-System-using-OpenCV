import cv2
import face_recognition
import sqlite3
import numpy as np
import pickle
import datetime

# ✅ Load student face encodings from DB
def load_known_faces():
    conn = sqlite3.connect("students.db")  # Database for students
    cursor = conn.cursor()

    cursor.execute("SELECT student_name, face_encoding FROM students")
    data = cursor.fetchall()
    conn.close()

    known_face_encodings = []
    known_face_names = []

    for student_name, encoding_blob in data:
        encoding = pickle.loads(encoding_blob)  # Convert from BLOB
        known_face_encodings.append(encoding)
        known_face_names.append(student_name)

    return known_face_encodings, known_face_names

# ✅ Mark attendance in database
def mark_attendance(name):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS attendance (name TEXT, timestamp TEXT)")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", (name, timestamp))
    
    conn.commit()
    conn.close()
    print(f"✅ Attendance marked for {name} at {timestamp}")

# ✅ Start Face Recognition for Student Attendance
def scan_faces():
    known_face_encodings, known_face_names = load_known_faces()
    
    cap = cv2.VideoCapture(0)
    print("📸 Scanning for students...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Camera not accessible.")
            break

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces and encode them
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            # Compare with known students
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                name = known_face_names[match_index]
                mark_attendance(name)  # 🟢 Mark attendance for student

            # Display name on frame
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Student Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_faces()
