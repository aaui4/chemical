from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import get_db

login_bp = Blueprint("login", __name__, url_prefix="/login")

@login_bp.route("/", methods=["GET", "POST"])
def login():
    # إذا الأدمن مسجل الدخول بالفعل، يدخل مباشرة
    if session.get("role") == "admin":
        return redirect(url_for("admin.dashboard"))
    
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")



        db = get_db()
        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]



            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("profile"))

        flash("اسم المستخدم أو كلمة المرور خاطئة", "error")

    return render_template("login/login.html", error=error)
