from flask import Blueprint, render_template, request, redirect, url_for
from database.auth import register_user as auth_register_user

register_bp = Blueprint("register", __name__, url_prefix="/register")

@register_bp.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        success, error = auth_register_user(username, email, password)

        if success:
            return redirect(url_for("login.login"))  # اسم الدالة في app.py
        else:
            return render_template("login/register.html", error=error)

    return render_template("login/register.html")
