import sqlite3
import os

# Force correct database path
TEACHER_DB_PATH = os.path.abspath(os.path.join(os.getcwd(), "frontend", "teachers.db"))

conn = sqlite3.connect(TEACHER_DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT email, unique_code FROM teachers")
rows = cursor.fetchall()

for row in rows:
    print(row)  # Print stored email and unique_code

conn.close()
