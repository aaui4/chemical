from flask import Blueprint, render_template, session, redirect, url_for
from database.db import get_db
from flask import request


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
def dashboard():
    # حماية الصفحة: فقط الـ admin
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    # بيانات المستخدم الحالي
    user_id = session.get("user_id")
    if user_id:
        user = db.execute("SELECT username, avatar FROM user WHERE id=?", (user_id,)).fetchone()
        if user:
            user = dict(user)
        else:
            user = {"username": "Admin", "avatar": "default.png"}
    else:
        user = {"username": "Admin", "avatar": "default.png"}

    # عدد المستخدمين
    users_count = db.execute("SELECT COUNT(*) as count FROM user").fetchone()["count"]

    # التفاعلات الجارية والمكتملة
    stats = db.execute("""
        SELECT
            SUM(CASE WHEN state='Ongoing' THEN 1 ELSE 0 END) AS ongoing,
            SUM(CASE WHEN state='Completed' THEN 1 ELSE 0 END) AS completed
        FROM reaction_results
    """).fetchone()
    ongoing_reactions = stats["ongoing"] or 0
    completed_reactions = stats["completed"] or 0

    # آخر النتائج
    reaction_results = db.execute("""
        SELECT
            cr.equation,
            rr.state,
            s.date,
            rr.energyReleased
        FROM reaction_results rr
        JOIN simulation s ON rr.simulation_id = s.id
        JOIN chemical_reactions cr ON s.reaction_id = cr.id
        ORDER BY rr.id DESC
        LIMIT 5
    """).fetchall()

    # آخر السجلات (Logs)
    logs = db.execute("""
        SELECT message FROM logs
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    db.close()

    return render_template(
        "admin/dashboard.html",
        user=user,
        users_count=users_count,
        ongoing_reactions=ongoing_reactions,
        completed_reactions=completed_reactions,
        reaction_results=reaction_results,
        logs=logs
    )
@admin_bp.route("/users")
def users():
    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    # بيانات المستخدم الحالي (نفس كود dashboard)
    user_id = session.get("user_id")
    if user_id:
        user = db.execute(
            "SELECT username, avatar FROM user WHERE id=?",
            (user_id,)
        ).fetchone()
        if user:
            user = dict(user)
        else:
            user = {"username": "Admin", "avatar": "default.png"}
    else:
        user = {"username": "Admin", "avatar": "default.png"}

    # جلب كل المستخدمين
    users = db.execute(
        "SELECT id, username, email, role FROM user"
    ).fetchall()

    db.close()

    return render_template(
        "admin/admin_user.html",
        users=users,
        user=user   
    )

@admin_bp.route("/user/<int:user_id>")
def user_profile(user_id):

    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE id = ?",
        (user_id,)
    ).fetchone()

    if not user:
        return "User not found", 404

    return render_template(
        "admin/view_user.html",
        user=user
    )

@admin_bp.route("/user/<int:user_id>/change-role", methods=["POST"])
def change_role(user_id):

    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    new_role = request.form.get("role")

    db = get_db()
    db.execute(
        "UPDATE user SET role = ? WHERE id = ?",
        (new_role, user_id)
    )
    db.commit()
    db.close()

    return redirect(url_for("admin.user_profile", user_id=user_id))

@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):

    if session.get("role") != "admin":
        return redirect(url_for("login.login"))

    db = get_db()

    # منع الأدمن من حذف نفسه
    if session.get("user_id") == user_id:
        db.close()
        return redirect(url_for("admin.user_profile", user_id=user_id))

    db.execute("DELETE FROM user WHERE id = ?", (user_id,))
    db.commit()
    db.close()

    return redirect(url_for("admin.users"))

