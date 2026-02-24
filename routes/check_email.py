from flask import Blueprint, request, jsonify
import sqlite3
import os

# إنشاء Blueprint خاص بهذه الوظيفة (check_email) لكي يمكن ربطها بتطبيق Flask
check_email_bp = Blueprint("check_email", __name__)


DB_FILE = os.path.join(os.path.dirname(__file__), "../database/chemical.db")

# دالة للحصول على اتصال بقاعدة البيانات
def get_db_connection():
    """
    تنشئ اتصالًا بقاعدة بيانات SQLite وتضبط row_factory
    لكي يمكن الوصول إلى الصفوف كـ dict (مفتاح=اسم العمود)
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# تعريف endpoint لفحص البريد الإلكتروني
@check_email_bp.route("/check-email", methods=["POST"])
def check_email():
    """
    هذه الدالة تتحقق إذا كان البريد الإلكتروني موجودًا في جدول user.
    تتلقى البريد عبر JSON وتعيد JSON يحتوي على {"exists": True/False}.
    """
    try:
        # قراءة البيانات المرسلة عبر JSON
        data = request.get_json(force=True)
        email = data.get("email", "").strip()  # إزالة الفراغات من البداية والنهاية

        # إذا لم يتم إرسال البريد الإلكتروني
        if not email:
            return jsonify({"exists": False})

        # فتح اتصال بقاعدة البيانات
        conn = get_db_connection()
        cursor = conn.cursor()

        # إنشاء جدول المستخدمين إذا لم يكن موجودًا بالفعل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        conn.commit()

        # البحث عن البريد الإلكتروني في الجدول
        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        exists = cursor.fetchone() is not None  # True إذا وجد البريد، False إذا لم يوجد

        # إعادة النتيجة على شكل JSON
        return jsonify({"exists": exists})

    except Exception as e:
        # طباعة الخطأ في الطرفية وإرجاع رسالة خطأ
        print("Error in /check-email:", e)
        return jsonify({"exists": False, "error": str(e)}), 500

    finally:
        # التأكد من إغلاق الاتصال بقاعدة البيانات دائمًا
        if 'conn' in locals():
            conn.close()
