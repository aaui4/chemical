from flask import Flask, request, render_template, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]
        flash("If this email exists, a reset link will be sent ")
        return redirect(url_for("forgot"))
    return render_template("login/forgot.html")