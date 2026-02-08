from flask import Blueprint, request, jsonify
import sqlite3
import os

check_username_bp = Blueprint("check_username", __name__)

DB_FILE = os.path.join(os.path.dirname(__file__), "../database/chemical.db")

def get_db_connection():
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(f"{DB_FILE} not found!")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@check_username_bp.route("/check-username", methods=["POST"])
def check_username():
    data = request.get_json(silent=True)
    if not data or "username" not in data:
        return jsonify({"exists": False, "error": "No username provided"}), 400
    
    username = data["username"].strip()
    if not username:
        return jsonify({"exists": False})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # إنشاء جدول إذا لم يكن موجودًا
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        conn.commit()
        # التحقق من وجود اسم المستخدم
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        exists = cursor.fetchone() is not None
        return jsonify({"exists": exists})
    finally:
        conn.close()
