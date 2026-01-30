from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret_key"

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('home.html')

# تسجيل الدخول
@app.route('/login')
def login():
    return render_template('login/login.html')

@app.route('/forgot')
def forgot():
    return render_template('login/forgot.html')

# تسجيل جديد
@app.route('/register')
def register():
    return render_template('login/register.html')

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