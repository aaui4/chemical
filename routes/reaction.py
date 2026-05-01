from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_babel import gettext as _

reaction = Blueprint('reaction', __name__)

# ===== USER: Add Reaction =====
@reaction.route('/add_reaction', methods=['GET', 'POST'])
def add_reaction():
    if 'user_id' not in session:
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        equation = request.form.get('equation')
        description = request.form.get('description')
        reaction_type = request.form.get('reaction_type', 'default')
        temperature = request.form.get('temperature')
        pressure = request.form.get('pressure')
        
        # جلب لون النتيجة من المستخدم
        result_color = request.form.get('result_color_text') or request.form.get('result_color') or '#ffffff'
        
        user_id = session['user_id']

        conn = sqlite3.connect('database/chemical.db')
        c = conn.cursor()

        # تخزين التفاعل مع result_color
        c.execute("""
            INSERT INTO pending_reactions (user_id, equation, description, type, temperature, pressure, result_color, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (user_id, equation, description, reaction_type, temperature, pressure, result_color))

        conn.commit()
        conn.close()

        flash(_("Reaction submitted for review"), "success")
        return redirect(url_for('simulation.simulation_page'))

    return render_template('reaction/add_reaction.html')


# ===== ADMIN: عرض التفاعلات المعلقة =====
@reaction.route('/admin/pending_reactions')
def pending_reactions():
    if 'user_id' not in session:
        return redirect(url_for('login.login'))
    
    conn = sqlite3.connect('database/chemical.db')
    c = conn.cursor()

    c.execute("""
        SELECT p.id, p.equation, p.description, p.type, p.temperature, p.pressure, 
               p.created_at, u.username, p.result_color
        FROM pending_reactions p
        JOIN user u ON p.user_id = u.id
        WHERE p.status = 'pending'
        ORDER BY p.created_at DESC
    """)
    reactions = c.fetchall()

    conn.close()

    return render_template('reaction/pending_reactions.html', reactions=reactions)


# ===== ADMIN: قبول التفاعل =====
@reaction.route('/accept/<int:id>')
def accept(id):
    conn = sqlite3.connect('database/chemical.db')
    c = conn.cursor()

    # جلب بيانات التفاعل مع result_color
    c.execute("""
        SELECT equation, description, type, temperature, pressure, result_color
        FROM pending_reactions 
        WHERE id = ? AND status = 'pending'
    """, (id,))
    reaction_data = c.fetchone()

    if reaction_data:
        # إضافة التفاعل إلى chemical_reactions مع result_color
        c.execute("""
            INSERT INTO chemical_reactions (equation, description, type, temperature, pressure, result_color)
            VALUES (?, ?, ?, ?, ?, ?)
        """, reaction_data)

        # تحديث حالة التفاعل في pending_reactions إلى 'accepted'
        c.execute("UPDATE pending_reactions SET status = 'accepted' WHERE id = ?", (id,))

        conn.commit()
        flash(_("Reaction accepted successfully!"), "success")
    else:
        flash(_("Reaction not found or already processed"), "error")

    conn.close()
    return redirect(url_for('reaction.pending_reactions'))


# ===== ADMIN: رفض التفاعل =====
@reaction.route('/reject/<int:id>')
def reject(id):
    conn = sqlite3.connect('database/chemical.db')
    c = conn.cursor()

    c.execute("UPDATE pending_reactions SET status = 'rejected' WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    flash(_("Reaction rejected"), "error")
    return redirect(url_for('reaction.pending_reactions'))