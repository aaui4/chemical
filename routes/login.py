from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import get_db

login_bp = Blueprint("login", __name__, url_prefix="/login")

@login_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        db = get_db()
        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            # حفظ البيانات في session
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            # إعادة التوجيه حسب الدور
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash("اسم المستخدم أو كلمة المرور خاطئة", "error")
    return render_template("login/login.html")
