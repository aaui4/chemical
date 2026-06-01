from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_babel import gettext as _
import re

reaction = Blueprint('reaction', __name__)

# دالة منع التكرار
def get_or_create_element(cursor, name, symbol, color=""):

    name = name.strip()
    symbol = symbol.strip().upper()
    symbol = symbol.strip().lower().replace("₂","2")
    symbol = symbol.strip().lower()

  # توحيد الحالات الشائعة
    if symbol in ["hcl(aq)", "hydrochloric acid"]:
      symbol = "hcl"

    cursor.execute("""
        SELECT id FROM chemical_elements
        WHERE LOWER(symbol) = LOWER(?)
    """, (symbol,))

    existing = cursor.fetchone()

    #  إذا موجود يرجع نفس الـ id
    if existing:
        return existing[0]

    #  إذا غير موجود ينشئ عنصر جديد
    cursor.execute("""
        INSERT INTO chemical_elements (name, symbol, default_color)
        VALUES (?, ?, ?)
    """, (name, symbol, color))

    return cursor.lastrowid


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
        gas_produced = int(request.form.get('gas_produced', 0))
        reactant1_color = request.form.get("reactant1_color", "")
        reactant2_color = request.form.get("reactant2_color", "")

        #  المتفاعلات
        reactant1_name = request.form.get("reactant1_name")
        reactant1_symbol = request.form.get("reactant1_symbol")
        reactant2_name = request.form.get("reactant2_name")
        reactant2_symbol = request.form.get("reactant2_symbol")

        result_color = request.form.get('result_color_text') or request.form.get('result_color') or '#ffffff'

        user_id = session['user_id']

        conn = sqlite3.connect('database/chemical.db')
        c = conn.cursor()

        #  إنشاء أو جلب العناصر
        reactant1_id = get_or_create_element( c, reactant1_name,  reactant1_symbol, reactant1_color)
        reactant2_id = get_or_create_element(c, reactant2_name, reactant2_symbol, reactant2_color)

        #  إذا كان Admin يضاف مباشرة
        if session.get("role") == "admin":
            c.execute("""
                INSERT INTO chemical_reactions
                (equation, description, type, temperature, pressure,gas_produced , result_color)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                   equation,
                   description,
                   reaction_type,
                   temperature,
                   pressure,
                   gas_produced,
                   result_color
               ))

            reaction_id = c.lastrowid
        else:
            c.execute("""
INSERT INTO chemical_reactions
(equation, description, type, temperature, pressure, gas_produced, result_color)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    equation,
    description,
    reaction_type,
    temperature,
    pressure,
    gas_produced,
    result_color
))

            reaction_id = c.lastrowid

        #  ربط المتفاعلات
        c.execute("INSERT INTO reaction_elements (reaction_id, element_id) VALUES (?, ?)", (reaction_id, reactant1_id))
        c.execute("INSERT INTO reaction_elements (reaction_id, element_id) VALUES (?, ?)", (reaction_id, reactant2_id))

        conn.commit()
        conn.close()

        flash(_("Reaction submitted for review"), "success")
        return redirect(url_for('simulation.simulation_page'))

    return render_template('reaction/add_reaction.html')
