from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import secrets
import os
from pathlib import Path
from config import Config
from database.db import close_db
from database.models import create_tables
from routes.login import login_bp
from routes.register import register_bp
from routes.check_email import check_email_bp
from routes.check_username import check_username_bp


# مستخدم وهمي للتجربة
user_data = {"username": "Asma", "avatar": "default.png"}

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(check_email_bp)
app.register_blueprint(check_username_bp)

mail = Mail(app)

# إنشاء مجلد التحميلات عند بدء التشغيل
def create_upload_folder():
    upload_path = Path(app.config['UPLOAD_FOLDER'])
    upload_path.mkdir(parents=True, exist_ok=True)
    print(f" مجلد التحميلات جاهز: {upload_path.absolute()}")

create_upload_folder()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/go-home')
def go_home():
    # هنا نستخدم اسم الدالة home، وليس اسم الملف
    return redirect(url_for('home'))
@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    if session.get("role") != "admin":
        return redirect(url_for("profile"))

    return render_template("admon-bord.html")


@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    if request.method == 'POST':
        user_email = request.form['email']
        token = secrets.token_urlsafe(16)
        reset_link = url_for('reset_password', token=token, _external=True)

        msg = Message("استرجاع كلمة السر",
                      sender="kindkiki9@gmail.com",
                      recipients=[user_email])
        msg.body = f"اضغطي على الرابط التالي لإعادة تعيين كلمة السر:\n{reset_link}"

        try:
            mail.send(msg)
            flash("تم إرسال رابط إعادة تعيين كلمة السر إلى بريدك الإلكتروني")
        except Exception as e:
            print(f" خطأ في إرسال البريد: {e}")
            flash("حدث خطأ أثناء إرسال البريد، حاول لاحقاً")

        return redirect(url_for('forgot'))

    return render_template('login/forgot.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['password']
        flash("تم تحديث كلمة السر بنجاح!")
        return redirect(url_for('login'))

    return """
    <form method="POST">
        <input type="password" name="password" placeholder="New Password" required>
        <button type="submit">Reset Password</button>
    </form>
    """

@app.route('/profile')
def profile():
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    return render_template('profile.html', user=user_data)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    global user_data

    username = request.form.get('username')
    file = request.files.get('avatar')

    if username:
        user_data['username'] = username

    if file and allowed_file(file.filename):
        try:
            # تأكد من وجود المجلد
            upload_folder = Path(app.config['UPLOAD_FOLDER'])
            upload_folder.mkdir(parents=True, exist_ok=True)
            
            # حفظ الملف
            filename = secure_filename(file.filename)
            # إضافة علامة زمنية لتجنب تكرار الأسماء
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_part = Path(filename).stem
            ext = Path(filename).suffix
            unique_filename = f"{name_part}_{timestamp}{ext}"
            
            filepath = upload_folder / unique_filename
            file.save(filepath)
            
            # حذف الصورة القديمة إذا لم تكن default.png
            if user_data['avatar'] != 'default.png':
                old_file = upload_folder / user_data['avatar']
                if old_file.exists():
                    old_file.unlink()
            
            user_data['avatar'] = unique_filename
            flash("تم تحديث الصورة الشخصية بنجاح!", "success")
            
        except Exception as e:
            print(f" خطأ في حفظ الصورة: {e}")
            flash("حدث خطأ أثناء حفظ الصورة", "error")

    elif file and not allowed_file(file.filename):
        flash("نوع الملف غير مسموح به. المسموح: PNG, JPG, JPEG, GIF", "error")

    if username:
        flash("تم تحديث اسم المستخدم بنجاح!", "success")

    return redirect(url_for('profile'))

@app.route('/search')
def search():
    return render_template('search/search.html')


@app.route('/reactants')
def reactants():
    return render_template('reactants/reactants.html')


@app.route('/settings')
def settings():
    return "Settings Page"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    print("بدء تشغيل التطبيق...")
    
    # إنشاء Application Context مؤقت
    with app.app_context():
        create_tables()  # إنشاء الجداول إذا لم تكن موجودة

    app.run(debug=True, host='0.0.0.0', port=5000)