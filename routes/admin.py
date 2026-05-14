from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from database.db import get_db
from flask import jsonify
from flask_babel import gettext as _

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# DASHBOARD

@admin_bp.route("/dashboard")
def dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))
    db = get_db()

    user_id = session.get("user_id")
    if user_id:
        user = db.execute("SELECT username, avatar FROM user WHERE id=?", (user_id,)).fetchone()
        user = dict(user) if user else {"username": "Admin", "avatar": "default.png"}
    else:
        user = {"username": "Admin", "avatar": "default.png"}

    users_count = db.execute("SELECT COUNT(*) as count FROM user").fetchone()["count"]

       
    total_experiments = db.execute("""
       SELECT COUNT(*) as count FROM simulation
       """).fetchone()["count"]

    reaction_results = db.execute("""
        SELECT cr.equation, rr.state, s.date
        FROM reaction_results rr
        JOIN simulation s ON rr.simulation_id = s.id
        JOIN chemical_reactions cr ON s.reaction_id = cr.id
        ORDER BY rr.id DESC
        LIMIT 5
    """).fetchall()


    chart_data_raw = db.execute("""SELECT strftime('%Y-%m-%d', s.date) as day, COUNT(*) as count FROM simulation s GROUP BY day ORDER BY day
    """).fetchall()

    chart_labels = [row["day"] for row in chart_data_raw]
    chart_data = [row["count"] for row in chart_data_raw]

    
    db.close()



    return render_template(
        "admin/dashboard.html",
        user=user,
        users_count=users_count,
        total_experiments=total_experiments,
        reaction_results=reaction_results,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


# USERS

@admin_bp.route("/users")
def users():
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    user_id = session.get("user_id")
    user = db.execute("SELECT username, avatar FROM user WHERE id=?", (user_id,)).fetchone()
    user = dict(user) if user else {"username": "Admin", "avatar": "default.png"}

    users = db.execute("SELECT id, username, email, role FROM user").fetchall()

    db.close()


    return render_template("admin/admin_user.html", users=users, user=user)


# USER PROFILE

@admin_bp.route("/user/<int:user_id>")
def user_profile(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    user = db.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()

    if not user:
        return "User not found", 404

    
    
    db.close()


    return render_template("admin/view_user.html", user=user)


# CHANGE ROLE

@admin_bp.route("/user/<int:user_id>/change-role", methods=["POST"])
def change_role(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    new_role = request.form.get("role")

    db = get_db()
    db.execute("UPDATE user SET role = ? WHERE id = ?", (new_role, user_id))
    db.close()

    return redirect(url_for("admin.user_profile", user_id=user_id))


# DELETE USER

@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    if session.get("user_id") == user_id:
        db.close()
        return redirect(url_for("admin.user_profile", user_id=user_id))

    db.execute("DELETE FROM user WHERE id = ?", (user_id,))
    db.close()

    return redirect(url_for("admin.users"))


# =========================
# ADD REACTION
# =========================
@admin_bp.route("/add_reaction", methods=["POST"])
def add_reaction():
    try:
        db = get_db()
        cursor = db.cursor()

        reactant1 = request.form.get("reactant1") or ""
        reactant2 = request.form.get("reactant2") or ""
        product = request.form.get("product") or ""
        equation = request.form.get("equation")

        reactant1_color = request.form.get("reactant1_color") or "#000000"
        reactant2_color = request.form.get("reactant2_color") or "#000000"
        product_color = request.form.get("product_color") or "#000000"
        # إنشاء reaction
        cursor.execute("INSERT INTO chemical_reactions (equation) VALUES (?)", (equation,))
        reaction_id = cursor.lastrowid

        # دالة
        def get_or_create_element(name, color):
            cursor.execute("SELECT id FROM chemical_elements WHERE name = ?", (name,))
            element = cursor.fetchone()

            if element:
                return element[0]

            symbol = name[:2].upper()

            cursor.execute("""
                INSERT INTO chemical_elements (name, symbol, default_color)
                VALUES (?, ?, ?)
            """, (name, symbol, color))

            return cursor.lastrowid

        # reactants
        if reactant1:
            id1 = get_or_create_element(reactant1, reactant1_color)
            cursor.execute("""
                INSERT INTO reaction_elements (reaction_id, element_id, role)
                VALUES (?, ?, ?)
            """, (reaction_id, id1, "reactant"))

        if reactant2:
            id2 = get_or_create_element(reactant2, reactant2_color)
            cursor.execute("""
                INSERT INTO reaction_elements (reaction_id, element_id, role)
                VALUES (?, ?, ?)
            """, (reaction_id, id2, "reactant"))

        # product
        if product:
            id3 = get_or_create_element(product, product_color)
            cursor.execute("""
                INSERT INTO reaction_elements (reaction_id, element_id, role)
                VALUES (?, ?, ?)
            """, (reaction_id, id3, "product"))
        db.commit()
        db.close()

        flash(_("Reaction added successfully"), "success")

    except Exception as e:
        print(e)
        flash(_("Error adding reaction: %(error)s", error=str(e)), "error")

    return redirect(url_for("admin.experiments"))


@admin_bp.route("/experiments")
def experiments():
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    user_id = session.get("user_id")
    if user_id:
        user = db.execute("SELECT username, avatar FROM user WHERE id=?", (user_id,)).fetchone()
        user = dict(user) if user else {"username": "Admin", "avatar": "default.png"}
    else:
        user = {"username": "Admin", "avatar": "default.png"}

    reactions = db.execute("""
        SELECT cr.id, cr.equation
        FROM chemical_reactions cr
        ORDER BY cr.id DESC
    """).fetchall()


    
    db.close()


    return render_template(
        "admin/experiments.html",
        user=user,   # لازم
        reactions=reactions,
    )

@admin_bp.route("/reaction/edit/<int:id>", methods=["GET", "POST"])
def edit_reaction(id):
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    if request.method == "POST":
        equation = request.form.get("equation")

        db.execute(
            "UPDATE chemical_reactions SET equation = ? WHERE id = ?",
            (equation, id)
        )
        
        db.commit()
        db.close()
        return redirect(url_for("admin.experiments"))

    reaction = db.execute(
        "SELECT * FROM chemical_reactions WHERE id = ?",
        (id,)
    ).fetchone()

    db.close()

    return render_template("admin/edit_reaction.html", reaction=reaction)

@admin_bp.route("/reaction/delete/<int:id>", methods=["POST"])
def delete_reaction(id):
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    db.execute("DELETE FROM chemical_reactions WHERE id = ?", (id,))
    db.commit()

    db.close()

    return redirect(url_for("admin.experiments"))


@admin_bp.route("/statistics")
def statistics():
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    # مثال: عدد التجارب حسب الحالة
    stats = db.execute("""
        SELECT state, COUNT(*) as count
        FROM reaction_results
        GROUP BY state
    """).fetchall()

    labels = [row["state"] for row in stats]
    data = [row["count"] for row in stats]

    
    db.close()


    return render_template(
        "admin/statistics.html",
        labels=labels,
        data=data
    )