import streamlit as st
import sqlite3
import hashlib
import re  # For email validation
import qrcode
from io import BytesIO

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("teachers.db")
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, 
            email TEXT UNIQUE,
            unique_code TEXT UNIQUE,
            subject TEXT,
            password TEXT
        )
    ''')

    # Check if 'name' column exists, if not, add it
    cursor.execute("PRAGMA table_info(teachers);")
    columns = [col[1] for col in cursor.fetchall()]
    if "name" not in columns:
        cursor.execute("ALTER TABLE teachers ADD COLUMN name TEXT;")
        conn.commit()

    conn.close()


# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Function to register a teacher
def register_teacher(name, email, unique_code, subject, password):
    if not is_valid_email(email):
        return "Invalid email format."
    
    if len(unique_code) != 10:
        return "Institute Unique Code must be exactly 10 characters long."

    conn = sqlite3.connect("teachers.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO teachers (name, email, unique_code, subject, password) VALUES (?, ?, ?, ?, ?)", 
                       (name, email, unique_code, subject, hash_password(password)))
        conn.commit()
        conn.close()
        return "success"
    except sqlite3.IntegrityError:
        conn.close()
        return "Email or Unique Code already exists."


# Function to generate a QR Code
def generate_qr(name, email, subject, unique_code):
    qr_data = f"Name: {name}\nTeacher Email: {email}\nSubject: {subject}\nUnique Code: {unique_code}"
    qr = qrcode.make(qr_data)

    qr_bytes = BytesIO()
    qr.save(qr_bytes, format="PNG")
    qr_bytes.seek(0)
    
    return qr_bytes  # Return QR image in byte format


# Function to display the signup page
def show_signup():
    # Initialize database
    init_db()

    st.title("📚 Teacher Account Creation")

    name = st.text_input("👤 Full Name")
    email = st.text_input("📧 Email")
    unique_code = st.text_input("🏫 Teacher's Unique Code (10-character code provided by the institute)")
    subject = st.selectbox("📖 Subject", ["Physics", "Maths", "FDA", "PPS", "Vedic Maths", "UHV", "EC"])
    password = st.text_input("🔒 Password", type="password")

    if st.button("Create Account"):
        if name and email and unique_code and subject and password:
            result = register_teacher(name, email, unique_code, subject, password)
            if result == "success":
                st.success("✅ Account created successfully!")

                # Generate QR Code
                qr_img = generate_qr(name, email, subject, unique_code)

                # Display QR Code
                st.image(qr_img, caption="📌 Your Unique QR Code", use_container_width=False)

                # Provide download button
                st.download_button(
                    label="📥 Download QR Code",
                    data=qr_img,
                    file_name=f"{email}_QR.png",
                    mime="image/png"
                )

            else:
                st.error(f"❌ {result}")
        else:
            st.warning("⚠️ Please fill all fields before submitting.")
