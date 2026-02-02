from flask import Flask, render_template, redirect, url_for, session
from database.db import close_db
from database.models import create_tables
from routes.login import login_user
from routes.register import register_user

app = Flask(__name__)
app.secret_key = "secret_key"
# انشاء  الجداول مرة واحدة
with app.app_context():
    create_tables()
    # اغلاق اتصال  بعد كل request
app.teardown_appcontext(close_db)
# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('home.html')

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    return render_template("admin/admon-bord.html")

# تسجيل الدخول
@app.route('/login', methods=["GET", "POST"])
def login():
    return login_user()

@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    return render_template('login/forgot.html')

# تسجيل جديد
@app.route('/register', methods=["GET", "POST"])
def register():
    return register_user()

# صفحة التفاعلات
@app.route('/search')
def search():
    return render_template('search/search.html')

# صفحة المحاكاة
@app.route('/reactants')
def reactants():
    return render_template('reactants/reactants.html')

# صفحة الملف الشخصي
@app.route('/profile')
def profile():
    return "User Profile Page"

# إعدادات المستخدم
@app.route('/settings')
def settings():
    return "Settings Page"

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)