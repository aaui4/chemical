import re
from werkzeug.security import generate_password_hash
from .db import get_db


def register_user(first_name, institution, username, email, password, role="user"):

    first_name = (first_name or "").strip()
    institution = (institution or "").strip()
    username = (username or "").strip()
    email = (email or "").strip()
    password = (password or "").strip()

    if not first_name or not institution or not username or not email or not password:
        return False, "All fields are required"

    # First name
    if not re.fullmatch(r'[A-Za-z]{3,9}', first_name):
        return False, "Invalid first name"

    # Institution
    if not institution:
        return False, "Institution is required"

    if not re.fullmatch(r'[A-Za-z0-9\s]+', institution):
        return False, "Invalid institution"

    words = institution.split()

    if len(words) < 3 or len(words) > 6:
        return False, "Institution must be 3–6 words"

    for num in re.findall(r'\d+', institution):
        if len(num) != 4:
            return False, "Only 4-digit numbers allowed"

    # Username
    if not re.fullmatch(r'[A-Za-z0-9_]{4,8}', username):
        return False, "Invalid username"

    # Email
    if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return False, "Invalid email"

    # Password
    if len(password) < 6 or not re.fullmatch(r'[A-Za-z0-9]+', password):
        return False, "Invalid password"

    db = get_db()

    if db.execute("SELECT 1 FROM user WHERE username = ?", (username,)).fetchone():
        return False, "Username already exists"

    if db.execute("SELECT 1 FROM user WHERE email = ?", (email,)).fetchone():
        return False, "Email already exists"

    hashed_password = generate_password_hash(password)

    try:
        db.execute("""
            INSERT INTO user
            (first_name, institution, username, email, password, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, institution, username, email, hashed_password, role))

        db.commit()
        return True, None

    except Exception as e:
        print("REGISTER ERROR:", e)
        return False, "Registration error"