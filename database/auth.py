import re
from werkzeug.security import generate_password_hash
from .db import get_db

def register_user(username, email, password, role="user"):
    if not username or not email or not password:
        return False, "جميع الحقول مطلوبة"
    
    if len(username) < 4 or len(username) > 8:
     return False, "اسم المستخدم يجب أن يكون بين 4 و 8 أحرف"

    if username.isdigit():
     return False, "اسم المستخدم لا يمكن أن يكون أرقام فقط"

    if not re.match(r'^[A-Za-z0-9_]+$', username):
     return False, "اسم المستخدم يحتوي على رموز غير مسموحة"


    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return False, "البريد الإلكتروني غير صالح"

    db = get_db()

    if db.execute("SELECT 1 FROM user WHERE username = ?", (username,)).fetchone():
        return False, "اسم المستخدم موجود مسبقًا"

    if db.execute("SELECT 1 FROM user WHERE email = ?", (email,)).fetchone():
        return False, "البريد الإلكتروني موجود مسبقًا"

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
        return False, "حدث خطأ أثناء التسجيل"
