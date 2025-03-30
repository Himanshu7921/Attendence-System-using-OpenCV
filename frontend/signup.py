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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            unique_code TEXT UNIQUE,
            subject TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Function to register a teacher
def register_teacher(email, unique_code, subject, password):
    if not is_valid_email(email):
        return "Invalid email format."
    
    if len(unique_code) != 10:
        return "Institute Unique Code must be exactly 10 characters long."

    conn = sqlite3.connect("teachers.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO teachers (email, unique_code, subject, password) VALUES (?, ?, ?, ?)", 
                       (email, unique_code, subject, hash_password(password)))
        conn.commit()
        conn.close()
        return "success"
    except sqlite3.IntegrityError:
        conn.close()
        return "Email or Unique Code already exists."

# Function to generate a QR Code
def generate_qr(email, unique_code):
    qr_data = f"Teacher Email: {email}\nUnique Code: {unique_code}"
    qr = qrcode.make(qr_data)

    # Convert QR code to BytesIO object for Streamlit display
    qr_bytes = BytesIO()
    qr.save(qr_bytes, format="PNG")
    qr_bytes.seek(0)
    
    return qr_bytes  # Return QR image in byte format

def parse_qr_data(qr_content):
    print(f"📜 Scanned QR Content: {qr_content}")  # Debug print
    
    try:
        qr_lines = qr_content.strip().split("\n")  # Split into lines
        email = qr_lines[0].split(": ")[1].strip()
        unique_code = qr_lines[1].split(": ")[1].strip()
        
        print(f"✅ Extracted Email: {email}, Unique Code: {unique_code}")  # Debugging
        
        return email, unique_code
    except IndexError:
        print("❌ Error extracting QR data. Check QR formatting.")
        return None, None

# Function to display the signup page
def show_signup():
    # Initialize database
    init_db()

    st.title("📚 Teacher Account Creation")

    email = st.text_input("📧 Email")
    unique_code = st.text_input("🏫 Teacher's Unique Code (10-character code provided by the institute)")
    subject = st.selectbox("📖 Subject", ["Physics", "Maths", "FDA", "PPS", "Vedic Maths", "UHV", "EC"])
    password = st.text_input("🔒 Password", type="password")

    if st.button("Create Account"):
        if email and unique_code and subject and password:
            result = register_teacher(email, unique_code, subject, password)
            if result == "success":
                st.success("✅ Account created successfully!")

                # Generate QR Code
                qr_img = generate_qr(email, unique_code)

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
