import sqlite3
from werkzeug.security import generate_password_hash
import os

# ============================
# مسار قاعدة البيانات
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "chemical.db")

# ============================
# الاتصال بقاعدة البيانات
# ============================
db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

# ============================
# إنشاء الجداول إذا لم تكن موجودة
# ============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL,
    avatar TEXT DEFAULT 'default.png'
)
""")

# ============================
# بيانات الأدمن
# ============================
admin_username = "admin"
admin_email = "admin@gmail.com"
admin_password = generate_password_hash("Admin@123")
admin_role = "admin"

# ============================
# التحقق من وجود الأدمن
# ============================
cursor.execute("SELECT * FROM user WHERE email = ?", (admin_email,))
if cursor.fetchone() is None:
    cursor.execute(
        "INSERT INTO user (username, email, password, role) VALUES (?, ?, ?, ?)",
        (admin_username, admin_email, admin_password, admin_role)
    )
    db.commit()
    print("✅ Admin created successfully")
else:
    print("⚠️ Admin already exists in the database")

# ============================
# إغلاق الاتصال
# ============================
db.close()
