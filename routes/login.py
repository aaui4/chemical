from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import get_db
from flask_babel import gettext as _

login_bp = Blueprint("login", __name__, url_prefix="/login")


@login_bp.route("/", methods=["GET", "POST"])
def login():

    # إذا الأدمن مسجل الدخول بالفعل
    if session.get("role") == "admin":
        return redirect(url_for("admin.dashboard"))


    if request.method == "POST":


        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        #  تحقق من الحقول
        if not username or not password:
            flash("All fields are required", "error")
            return render_template("login/login.html")

        db = get_db()

        user = db.execute(
            "SELECT * FROM user WHERE username = ?",
            (username,)
        ).fetchone()

        #  تحقق آمن (لا نكشف السبب)
        if user and check_password_hash(user["password"], password):

            session.clear()  # حماية إضافية
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]



            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("profile"))

        flash(_("Incorrect username or password"), "error")

    return render_template("login/login.html")