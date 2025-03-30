import streamlit as st
import sys
import os

# Ensure the backend module path is included
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import login
import signup
from student_registration.student_registration import main as student_registration_main

# Streamlit Page Config
st.set_page_config(page_title="Teacher Portal", page_icon="🔑", layout="centered")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Signup (Faculty)", "Mark Attendence", "Student Registration"])

# Display the selected page
if page == "Mark Attendence":
    login.show_login()
elif page == "Signup (Faculty)":
    signup.show_signup()
elif page == "Student Registration":
    student_registration_main()