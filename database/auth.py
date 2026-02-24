import re
from werkzeug.security import generate_password_hash
from .db import get_db

def register_user(username, email, password, role="user"):
    # إزالة الفراغات الزائدة
    username = (username or "").strip()
    email = (email or "").strip()
    password = (password or "").strip()

    # 1️⃣ الحقول مطلوبة
    if not username or not email or not password:
        return False, "جميع الحقول مطلوبة"

    # 2️⃣ اسم المستخدم
    if not username.isascii():
        return False, "اسم المستخدم يجب أن يحتوي على حروف لاتينية فقط"
    if username.isdigit():
        return False, "اسم المستخدم لا يمكن أن يكون أرقام فقط"
    if not re.fullmatch(r'[A-Za-z0-9_]{4,8}', username):
        return False, "اسم المستخدم يجب أن يكون بين 4 و 8 أحرف ويحتوي فقط على حروف وأرقام و _"

    # 3️⃣ البريد الإلكتروني
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.fullmatch(email_regex, email):
        return False, "البريد الإلكتروني غير صالح"

    # 4️⃣ كلمة المرور
    if len(password) < 6:
        return False, "كلمة المرور يجب أن تكون 6 أحرف على الأقل"
    if not re.fullmatch(r'[A-Za-z0-9]+', password):
        return False, "كلمة المرور يمكن أن تحتوي على أحرف وأرقام فقط"

    db = get_db()

    # 5️⃣ التحقق من التكرار
    if db.execute("SELECT 1 FROM user WHERE username = ?", (username,)).fetchone():
        return False, "اسم المستخدم موجود مسبقًا"
    
    if db.execute("SELECT 1 FROM user WHERE email = ?", (email,)).fetchone():
        return False, "البريد الإلكتروني موجود مسبقًا"

    # 6️⃣ تشفير كلمة المرور وإدخال المستخدم
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
    