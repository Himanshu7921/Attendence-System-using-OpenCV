import streamlit as st
import cv2
import re
import sqlite3
import face_recognition
import numpy as np
import pickle
import datetime
import os
import pandas as pd
from signup import parse_qr_data

# Database Paths
DB_PATH = os.path.abspath("students.db")
TEACHER_DB_PATH = os.path.abspath("teachers.db")
ATTENDANCE_DB_PATH = os.path.abspath("attendance.db")
EXCEL_FILE_PATH = os.path.abspath("attendance.xlsx")

# Initialize state variables globally
if "close_attendance" not in st.session_state:
    st.session_state.close_attendance = False
if "attendance_done" not in st.session_state:
    st.session_state.attendance_done = False
if "recognized_students" not in st.session_state:
    st.session_state.recognized_students = set()

# Function to verify teacher credentials
def verify_teacher_qr(email, unique_code):
    with sqlite3.connect(TEACHER_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM teachers WHERE email = ? AND unique_code = ?", (email, unique_code))
        return cursor.fetchone() is not None

# Function to scan QR code
def scan_qr_code():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    st.warning("📷 Scanning for QR Code...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Camera not accessible.")
            break

        data, _, _ = detector.detectAndDecode(frame)
        if data:
            email_match = re.search(r"Teacher Email:\s*([\w.\-]+@[\w.\-]+)", data)
            code_match = re.search(r"Unique Code:\s*([\w\d]+)", data)

            if email_match and code_match:
                email = email_match.group(1)
                unique_code = code_match.group(1)
                st.success(f"✅ QR Code Detected for {email}")
                parse_qr_data(data)
                cap.release()
                cv2.destroyAllWindows()
                return email, unique_code
            else:
                st.error("❌ Invalid QR Code Format.")
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return None, None

# Load known student faces
def load_known_faces():
    known_face_encodings, known_face_names = [], []
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_name, face_encoding FROM students")
        for student_name, encoding_blob in cursor.fetchall():
            known_face_encodings.append(pickle.loads(encoding_blob))
            known_face_names.append(student_name)
    return known_face_encodings, known_face_names

# Mark attendance (only first entry remains)
def mark_attendance(name):
    timestamp = datetime.datetime.now()
    formatted_date = timestamp.strftime("%d-%m-%Y")  # Format: 30-03-2025
    formatted_time = timestamp.strftime("%I:%M %p")  # Format: 08:21 PM

    with sqlite3.connect(ATTENDANCE_DB_PATH) as conn:
        cursor = conn.cursor()

        # ✅ Drop the old table if it exists (Only once if needed)
        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "date" not in columns or "time" not in columns:
            cursor.execute("DROP TABLE IF EXISTS attendance")  # ⚠️ Removes old structure
            cursor.execute("""
                CREATE TABLE attendance (
                    name TEXT PRIMARY KEY,  
                    date TEXT,
                    time TEXT
                )
            """)

        # ✅ Insert only the first entry per student (prevents duplicates)
        cursor.execute("""
            INSERT OR IGNORE INTO attendance (name, date, time) VALUES (?, ?, ?)
        """, (name, formatted_date, formatted_time))

        conn.commit()

# Export unique attendance with the oldest timestamp
def export_attendance_to_excel():
    with sqlite3.connect(ATTENDANCE_DB_PATH) as conn:
        df = pd.read_sql("SELECT name, date, time FROM attendance", conn)

        # ✅ Save as Excel with proper formatting
        df.to_excel(EXCEL_FILE_PATH, index=False)

    return EXCEL_FILE_PATH


# Scan and recognize student faces
def scan_faces():
    known_face_encodings, known_face_names = load_known_faces()
    cap = cv2.VideoCapture(0)
    
    st.warning("📸 Scanning for students... Click '🛑 Stop Attendance' to finish.")
    
    if st.button("🛑 Stop Attendance"):
        st.session_state.close_attendance = True
    
    while not st.session_state.close_attendance:
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Camera not accessible.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            if True in matches:
                name = known_face_names[matches.index(True)]
                if name not in st.session_state.recognized_students:
                    st.session_state.recognized_students.add(name)
                    mark_attendance(name)
                    st.success(f"✅ Attendance Marked for {name}")

    cap.release()
    cv2.destroyAllWindows()
    
    st.session_state.attendance_done = True

# Show login page
def show_login():
    st.title("🔑 Teacher Login")

    if "attendance_done" not in st.session_state:
        st.session_state.attendance_done = False
    if "close_attendance" not in st.session_state:
        st.session_state.close_attendance = False

    if st.button("📸 Scan QR Code"):
        email, unique_code = scan_qr_code()
        if email and unique_code and verify_teacher_qr(email, unique_code):
            st.success("✅ Teacher Login Successful!")
            st.session_state.close_attendance = False
            scan_faces()
            st.session_state.attendance_done = True
        else:
            st.error("❌ Teacher Not Registered or Invalid Unique Code.")

    if st.session_state.attendance_done:
        st.success("✅ Attendance has been recorded.")
    
    if st.button("📥 Download Attendance Report"):
        file_path = export_attendance_to_excel()
        with open(file_path, "rb") as file:
            st.download_button(
                label="📂 Download Excel",
                data=file,
                file_name="attendance.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Run the login function
if __name__ == "__main__":
    show_login()