from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
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
from database.db import get_db, close_db







# مستخدم وهمي للتجربة
user_data = {"username": "Asma", "avatar": "default.png"}

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(check_email_bp)
app.register_blueprint(check_username_bp)
app.register_blueprint(admin_bp)






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
        return redirect(url_for('login.login'))

    return """
    <form method="POST">
        <input type="password" name="password" placeholder="New Password" required>
        <button type="submit">Reset Password</button>
    </form>
    """

@app.route('/profile')
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login.login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()  # يفترض أنك تستخدم row_factory = sqlite3.Row
    if not user:
        flash("المستخدم غير موجود")
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

        # حذف الصورة القديمة إذا لم تكن default
        cursor.execute("SELECT avatar FROM user WHERE id = ?", (user_id,))
        old_avatar = cursor.fetchone()["avatar"]
        if old_avatar != 'default.png':
            old_path = Path(app.config['UPLOAD_FOLDER']) / old_avatar
            if old_path.exists():
                old_path.unlink()

    # تحديث قاعدة البيانات
    if username and avatar_filename:
        cursor.execute("UPDATE user SET username = ?, avatar = ? WHERE id = ?", (username, avatar_filename, user_id))
    elif username:
        cursor.execute("UPDATE user SET username = ? WHERE id = ?", (username, user_id))
    elif avatar_filename:
        cursor.execute("UPDATE user SET avatar = ? WHERE id = ?", (avatar_filename, user_id))

    db.commit()
    flash("تم تحديث البروفايل بنجاح!", "success")
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
