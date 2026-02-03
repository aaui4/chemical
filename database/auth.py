from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

def register_user(username, email, password, role="user"):
    if not username or not email or not password:
        return False

    db = get_db()
    hashed_password = generate_password_hash(password)

    try:
        db.execute("""
            INSERT INTO user (username, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, hashed_password, role))
        db.commit()
        return True
    except Exception as e:
        print("REGISTER ERROR:", e)  # ← ضروري أثناء التطوير
        return False

def login_user(username, password):
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE username = ?",
        (username,)
    ).fetchone()

    if user and check_password_hash(user["password"], password):
        return dict(user)
    return None

