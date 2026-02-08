from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from database.db import get_db

login_bp = Blueprint("login", __name__, url_prefix="/login")

@login_bp.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("home"))
        else:
            error = "اسم المستخدم أو كلمة السر غير صحيحة"
    return render_template("login/login.html", error=error)
