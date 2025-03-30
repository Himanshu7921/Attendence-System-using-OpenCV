import streamlit as st
import cv2
import face_recognition
import numpy as np
import sqlite3
import pickle
import os
from PIL import Image

# ✅ Ensure Database Path is Correct
DB_PATH = os.path.join(os.getcwd(), "students.db")

# ✅ Initialize the Database
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            branch TEXT NOT NULL,
            reg_number TEXT UNIQUE NOT NULL,
            face_encoding BLOB NOT NULL
        )
        """)
        conn.commit()
        conn.close()

        # ✅ Check if the database file was created
        if os.path.exists(DB_PATH):
            print(f"✅ Database initialized successfully at {DB_PATH}")
        else:
            print("❌ Database file not created!")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")

# ✅ Save Student Face Encoding to Database
def save_student(name, branch, reg_number, encoding):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        encoding_blob = pickle.dumps(encoding)  # Convert to BLOB
        cursor.execute("INSERT INTO students (student_name, branch, reg_number, face_encoding) VALUES (?, ?, ?, ?)",
                       (name, branch, reg_number, encoding_blob))
        conn.commit()
        conn.close()
        st.success(f"✅ {name} registered successfully!")
    
    except sqlite3.IntegrityError:
        st.error(f"❌ Registration number {reg_number} already exists!")
    except Exception as e:
        st.error(f"❌ Database error: {e}")

# ✅ Capture Face and Auto-Register Student using Streamlit Camera
def capture_and_register(name, branch, reg_number, image):
    # Convert PIL image to OpenCV format
    image = np.array(image)
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    face_locations = face_recognition.face_locations(frame_rgb)
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

    if face_encodings:
        encoding = face_encodings[0]
        save_student(name, branch, reg_number, encoding)  # Auto-save
    else:
        st.error("❌ No face detected! Try again.")

# ✅ Streamlit UI
def main():
    st.title("📸 Student Registration")

    init_db()  # Ensure database is created

    student_name = st.text_input("Enter Student Name")
    branch = st.text_input("Enter Branch")
    reg_number = st.text_input("Enter Registration Number")

    # ✅ Streamlit Camera Input
    uploaded_image = st.camera_input("Capture Your Face")

    if st.button("Register"):
        if student_name and branch and reg_number and uploaded_image:
            image = Image.open(uploaded_image)
            capture_and_register(student_name, branch, reg_number, image)  # Capture & auto-save
        else:
            st.error("❌ Please enter all details (Name, Branch, Registration Number) and capture your face.")

    # ✅ Debug: Check if the database exists
    if os.path.exists(DB_PATH):
        st.success(f"✅ Database is located at: {DB_PATH}")
    else:
        st.error("❌ Database file is missing!")

if __name__ == "__main__":
    main()
