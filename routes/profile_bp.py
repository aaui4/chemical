from flask import Blueprint, render_template, session, redirect, url_for
from database.db import get_db

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route("/", methods=['GET'])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    
    user_id = session["user_id"]
    db = get_db()
    cursor = db.cursor()
    
    # 1️⃣ عدد المحاكيات
    cursor.execute("SELECT COUNT(*) FROM simulation WHERE user_id = ?", (user_id,))
    saved_simulations_count = cursor.fetchone()[0] or 0

    # 2️⃣ آخر تفاعل
    cursor.execute("""
        SELECT s.result
        FROM simulation s
        WHERE s.user_id = ?
        ORDER BY s.date DESC
        LIMIT 1
    """, (user_id,))
    last_reaction = cursor.fetchone()
    last_reaction_text = last_reaction[0] if last_reaction else "No reactions yet"

    # 3️⃣ إجمالي التجارب
    total_experiments_count = saved_simulations_count

    # بيانات المستخدم
    cursor.execute("SELECT username, email, avatar FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    user_data = {
        'username': user[0] if user else '',
        'email': user[1] if user else '',
        'avatar': user[2] if user else ''
    }

    return render_template(
        "profile.html",
        user=user_data,
        saved_simulations_count=saved_simulations_count,
        last_reaction=last_reaction_text,
        total_experiments_count=total_experiments_count
    )
