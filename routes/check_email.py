from flask import Blueprint, request, jsonify
import sqlite3
import os

check_email_bp = Blueprint("check_email", __name__)

# مسار قاعدة البيانات بالنسبة لمكان الملف
DB_FILE = os.path.join(os.path.dirname(__file__), "../database/chemical.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@check_email_bp.route("/check-email", methods=["POST"])
def check_email():
    try:
        data = request.get_json(force=True)
        email = data.get("email", "").strip()
        if not email:
            return jsonify({"exists": False})

        conn = get_db_connection()
        cursor = conn.cursor()

        # إنشاء جدول إذا لم يكن موجود
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        conn.commit()

        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        exists = cursor.fetchone() is not None
        return jsonify({"exists": exists})

    except Exception as e:
        print("Error in /check-email:", e)
        return jsonify({"exists": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()
