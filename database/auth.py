from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

def register_user(username, email, password, role="user"):
    # التأكد من أن جميع الحقول موجودة
    if not username or not email or not password:
        return False

    db = get_db()
    cursor = db.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("""
            INSERT INTO user (username, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, hashed_password, role))
        db.commit()
        return True
    except:
        return False

def login_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user["password"], password):
        return dict(user)
    return None
