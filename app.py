from flask import Blueprint, Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash  # 🔥 أضف هذا السطر
import secrets
import os
from pathlib import Path
from config import Config
from database.models import create_tables
from routes.login import login_bp
from routes.register import register_bp
from routes.check_email import check_email_bp
from routes.check_username import check_username_bp
from routes.admin import admin_bp
from routes.simulation import simulation_bp
from database.db import get_db, close_db
from routes.compound import compound_bp
from routes.reaction import reaction
from datetime import datetime, timedelta

from flask import Flask, request, session
from flask_babel import Babel
from flask_babel import gettext as _

app = Flask(__name__)
app.config.from_object(Config)

# ===== Babel =====
def get_locale():
    return session.get('lang', 'en')

babel = Babel(app, locale_selector=get_locale)

# ===== حفظ اللغة =====
@app.before_request
def set_language():
    lang = request.args.get('lang')
    if lang:
        session['lang'] = lang

# ===== مهم: بعد تعريف get_locale =====
@app.context_processor
def inject_globals():
    return dict(get_locale=get_locale)


app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(check_email_bp)
app.register_blueprint(check_username_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(simulation_bp)
app.register_blueprint(compound_bp)
app.register_blueprint(reaction)

mail = Mail(app)

# إنشاء مجلد التحميلات عند بدء التشغيل
def create_upload_folder():
    upload_path = Path(app.config['UPLOAD_FOLDER'])
    upload_path.mkdir(parents=True, exist_ok=True)
    print(f" The upload folder is ready:{upload_path.absolute()}")

create_upload_folder()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/go-home')
def go_home():
    return redirect(url_for('home'))

# ========== حل مشكلة الرابط للهاتف (بدون netifaces) ==========
import socket
import subprocess
import re

def get_local_ip():
    """الحصول على IP الحقيقي للجهاز في الشبكة - طريقة تعمل على Windows"""
    try:
        # الطريقة الأولى: باستخدام socket (تصلح لمعظم الحالات)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith('127.'):
            return ip
    except:
        pass
    
    # الطريقة الثانية: باستخدام ipconfig (خاصة بـ Windows)
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        output = result.stdout
        
        # البحث عن IPv4 Address
        pattern = r'IPv4 Address[ .]+: (\d+\.\d+\.\d+\.\d+)'
        matches = re.findall(pattern, output)
        
        for ip in matches:
            # استبعاد الـ IPs الخاصة
            if not ip.startswith('127.') and not ip.startswith('169.254'):
                return ip
    except:
        pass
    
    # إذا فشل كل شيء، نرجع localhost
    return "127.0.0.1"

# الحصول على IP الحقيقي مباشرة عند بدء التشغيل
REAL_IP = get_local_ip()
SERVER_BASE_URL = f"http://{REAL_IP}:5000"
print(f"✓ Server will use: {SERVER_BASE_URL}")

# دالة لإنشاء جدول التوكنات إذا لم يكن موجوداً
def create_password_resets_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0
        )
    ''')
    db.commit()
    db.close()

# استدعاء الدالة عند بدء التشغيل
with app.app_context():
    create_password_resets_table()

@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    if request.method == 'POST':
        user_email = request.form['email']
        
        # التحقق إذا كان الإيميل موجود في قاعدة البيانات
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM user WHERE email = ?", (user_email,))
        user = cursor.fetchone()
        
        if user:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)  # صلاحية ساعة واحدة
            
            # حفظ التوكن في قاعدة البيانات
            cursor.execute(
                "INSERT INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)",
                (user_email, token, expires_at)
            )
            db.commit()
            
            # بناء الرابط يدوياً باستخدام IP الحقيقي
            reset_link = f"{SERVER_BASE_URL}/reset-password/{token}"
            
            print(f"🔗 Reset link sent: {reset_link}")
            print(f"📧 To: {user_email}")
            
            msg = Message(
                _("Password Reset"),
                sender="kindkiki9@gmail.com",
                recipients=[user_email]
            )
            
            msg.body = f"""
            {_('Click the following link to reset your password (valid for 1 hour):')}

            {reset_link}

            {_('If you did not request this, please ignore this email.')}
            """
            
            try:
                mail.send(msg)
                flash(_("A password reset link has been sent to your email"), "success")
            except Exception as e:
                print(f"خطأ في إرسال البريد: {e}")
                flash(_("An error occurred while sending the email. Please try again later"), "error")
        else:
            # لأسباب أمنية، نعطي نفس الرسالة حتى لو الإيميل غير موجود
            flash(_("If this email exists, a reset link will be sent"), "info")
        
        db.close()
        return redirect(url_for('forgot'))
    
    return render_template('login/forgot.html')

# ========== دالة reset_password المعدلة (الحل النهائي) ==========
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    print(f"🔐 Accessing reset password with token: {token}")
    
    # التحقق من صحة التوكن
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT email, expires_at, used 
        FROM password_resets 
        WHERE token = ? AND used = 0 AND expires_at > ?
    ''', (token, datetime.now()))
    
    reset_request = cursor.fetchone()
    
    if not reset_request:
        db.close()
        flash(_("Invalid or expired reset link. Please request a new one."), "error")
        return redirect(url_for('forgot'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        
        # 🔥 التعديل المهم: تشفير كلمة المرور بنفس طريقة التسجيل
        hashed_password = generate_password_hash(new_password)
        
        # تحديث كلمة المرور المشفرة في جدول المستخدمين
        cursor.execute(
            "UPDATE user SET password = ? WHERE email = ?",
            (hashed_password, reset_request['email'])
        )
        
        # تعليم التوكن كمستخدم
        cursor.execute(
            "UPDATE password_resets SET used = 1 WHERE token = ?",
            (token,)
        )
        
        db.commit()
        db.close()
        
        flash(_("Password updated successfully! Please login with your new password."), "success")
        return redirect(url_for('login.login'))
    
    db.close()
    return render_template('login/reset_password.html', token=token)

@app.route('/profile')
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login.login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    db.close()
    if not user:
        flash("User not found")
        return redirect(url_for("login.login"))

    return render_template("profile.html", user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login.login"))

    db = get_db()
    cursor = db.cursor()

    username = request.form.get('username')
    file = request.files.get('avatar')
    avatar_filename = None

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_part = Path(filename).stem
        ext = Path(filename).suffix
        avatar_filename = f"{name_part}_{timestamp}{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename))

        cursor.execute("SELECT avatar FROM user WHERE id = ?", (user_id,))
        old_avatar = cursor.fetchone()["avatar"]
        if old_avatar and old_avatar != 'default.png':
            old_path = Path(app.config['UPLOAD_FOLDER']) / old_avatar
            if old_path.exists():
                old_path.unlink()

    if username and avatar_filename:
        cursor.execute("UPDATE user SET username = ?, avatar = ? WHERE id = ?", (username, avatar_filename, user_id))
    elif username:
        cursor.execute("UPDATE user SET username = ? WHERE id = ?", (username, user_id))
    elif avatar_filename:
        cursor.execute("UPDATE user SET avatar = ? WHERE id = ?", (avatar_filename, user_id))

    if username:
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user and existing_user["id"] != user_id:
            flash("Username already exists!", "error")
            return redirect(url_for('profile'))

    db.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for('profile'))

@app.route('/delete-avatar', methods=['POST'])
def delete_avatar():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login.login"))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT avatar FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if user and user["avatar"]:
        avatar = user["avatar"]

        avatar_path = Path(app.config['UPLOAD_FOLDER']) / avatar
        if avatar_path.exists():
            avatar_path.unlink()

        cursor.execute("UPDATE user SET avatar = NULL WHERE id = ?", (user_id,))
        db.commit()

        flash("Avatar deleted successfully", "success")

    return redirect(url_for('profile'))

@app.route('/settings')
def settings():
    return "Settings Page"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))

@app.context_processor
def inject_notifications():
    conn = sqlite3.connect('database/chemical.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM pending_reactions WHERE status='pending'")
    count = c.fetchone()[0]

    conn.close()

    return dict(pending_count=count)

# تصحيح requests
import requests

def get_compound_data(name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/JSON"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        info = data['PC_Compounds'][0]

        return {
            "name": name,
            "cid": info.get("id", {}).get("id", {}).get("cid"),
        }
    except:
        return None

if __name__ == "__main__":
    print("=" * 50)
    print(" Starting the application...")
    print("=" * 50)
    
    with app.app_context():
        create_tables()
        print("✓ Database tables created/verified")
    
    print("\n" + "=" * 50)
    print(f" للوصول من الهاتف: http://{REAL_IP}:5000")
    print(f" للوصول من نفس الكمبيوتر: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)