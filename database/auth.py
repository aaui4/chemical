import re
from werkzeug.security import generate_password_hash
from .db import get_db

def register_user(username, email, password, role="user"):
    # إزالة الفراغات الزائدة
    username = (username or "").strip()
    email = (email or "").strip()
    password = (password or "").strip()

    #  الحقول مطلوبة
    if not username or not email or not password:
        return False, "All fields are required"

    #  اسم المستخدم
    if not username.isascii():
        return False, "Username must contain only ASCII characters"
    if username.isdigit():
        return False, "Username cannot contain only numbers"
    if not re.fullmatch(r'[A-Za-z0-9_]{4,8}', username):
        return False, "Username must be between 4 and 8 characters long and can only contain letters, numbers, and underscores"

    #  البريد الإلكتروني
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.fullmatch(email_regex, email):
        return False, "Email is invalid"

    #  كلمة المرور
    if len(password) < 6:
        return False, "The password must be at least 6 characters long."
    if not re.fullmatch(r'[A-Za-z0-9]+', password):
        return False, "The password can only contain letters and numbers."

    db = get_db()

    #  التحقق من التكرار
    if db.execute("SELECT 1 FROM user WHERE username = ?", (username,)).fetchone():
        return False, "Username already exists"
    
    if db.execute("SELECT 1 FROM user WHERE email = ?", (email,)).fetchone():
        return False, "Email already exists"

    # 6️ تشفير كلمة المرور وإدخال المستخدم
    hashed_password = generate_password_hash(password)

    try:
        db.execute(
            "INSERT INTO user (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, hashed_password, role)
        )
        db.commit()
        return True, None
    except Exception as e:
        print("REGISTER ERROR:", e)
        return False, "An error occurred during registration"
    