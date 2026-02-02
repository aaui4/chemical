from flask import render_template, request, redirect, url_for
from database.auth import register_user as auth_register_user

def register_user():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if auth_register_user(username, email, password):
            return redirect(url_for("login"))
        else:
            return render_template(
                "login/register.html",
                error="Username or email already exists or fields are empty"
            )

    return render_template("login/register.html")