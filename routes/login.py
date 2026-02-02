from flask import render_template, request, redirect, url_for, session
from database.auth import login_user as auth_login_user

def login_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = auth_login_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            # إذا admin يروح للوحة التحكم
            if user["role"] == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("home.html"))

        return render_template("login/login.html", error="Username or password incorrect")

    return render_template("login/login.html")