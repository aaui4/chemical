from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database.db import get_db
from datetime import datetime
import random
from flask import flash
from flask_babel import gettext as _


simulation_bp = Blueprint("simulation", __name__, url_prefix="/simulation")


# قاموس الألوان حسب نوع التفاعل
REACTION_COLORS = {
    'neutralization': 'transparent',
    'precipitation': 'white',
    'complex': 'blue',
    'indicator': 'pink',
    'gas': 'bubbly',
    'default': 'transparent'
}

# أوصاف النتائج حسب نوع التفاعل (سيتم استخدامها فقط إذا لم يوجد وصف في قاعدة البيانات)
REACTION_DESCRIPTIONS = {
    'neutralization': 'Neutralization reaction completed - clear solution',
    'precipitation': 'Precipitate formed',
    'complex': 'Color changed to blue - complex formed',
    'indicator': 'Color changed to pink - indicator reaction',
    'gas': 'Gas bubbles released',
    'default': 'Reaction completed successfully'
}

@simulation_bp.route("/", methods=["GET"])
def simulation_page():
    db = get_db()
    cursor = db.cursor()
    # جلب جميع العناصر الكيميائية
    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements ORDER BY name")
    reactants = cursor.fetchall()
    return render_template("simulation/simulation.html", reactants=reactants)

@simulation_bp.route("/start", methods=["POST"])
def start_simulation():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    db = get_db()
    cursor = db.cursor()

    # استلام البيانات من الفورم
    reactant1_id = request.form["reactant1"]
    reactant2_id = request.form["reactant2"]
    # منع اختيار نفس المادة مرتين
    if reactant1_id == reactant2_id:
        flash("⚠️ " + _("You cannot select the same reactant twice."), "error")
        return redirect(url_for("simulation.simulation_page"))

    quantity1 = float(request.form.get("quantity1", 0))
    quantity2 = float(request.form.get("quantity2", 0))
    temperature = float(request.form.get("temperature", 25))

    # جلب معلومات العنصر الأول
    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements WHERE id = ?", (reactant1_id,))
    reactant1 = cursor.fetchone()
    
    # جلب معلومات العنصر الثاني
    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements WHERE id = ?", (reactant2_id,))
    reactant2 = cursor.fetchone()


    # ===== إضافة التفاعل الغازي المحدد =====
    gas_produced = 0
    precipitate = 0
    result_color = 'transparent'
    reaction_type = 'default'
    description = REACTION_DESCRIPTIONS['default']

    if not reactant1 or not reactant2:
        return "Error: Reactants not found", 404

    # البحث عن تفاعل يحتوي على كلا العنصرين
    cursor.execute("""
        SELECT r.id, r.equation, r.type, r.result_color, r.gas_produced, 
               r.precipitate, r.min_temp, r.temperature, r.pressure
        FROM chemical_reactions r
        WHERE r.id IN (
            SELECT reaction_id FROM reaction_elements WHERE element_id = ?
        )
        AND r.id IN (
            SELECT reaction_id FROM reaction_elements WHERE element_id = ?
        )
    """, (reactant1_id, reactant2_id))

    reaction = cursor.fetchone()

    # متغيرات التفاعل
    reaction_id = None
    equation = f"{reactant1[2]} + {reactant2[2]} → Product"

    min_temp = 20
    opt_temp = 25
    pressure = 1.0
    description = REACTION_DESCRIPTIONS['default']
    temp_message = ""
    result_text = ""

    if reaction:
        # تفاعل موجود
        reaction_id, equation, reaction_type, result_color, gas_produced, precipitate, min_temp, opt_temp, pressure = reaction
        
        # التحقق من تأثير درجة الحرارة
        if temperature < min_temp:
            temp_message = _("⚠️ Temperature too low! Reaction needs at least %(temp)s°C", temp=min_temp)
            result_text = _("Slow reaction at %(temp)s°C", temp=temperature)
        elif temperature > opt_temp + 30:
            temp_message = _("⚠️ Temperature too high! Optimal temperature is %(temp)s°C", temp=opt_temp)
            result_text = _("Fast reaction at %(temp)s°C", temp=temperature)
        else:
            temp_message = _("✅ Optimal temperature (%(temp)s°C)", temp=temperature)
            result_text = _("Normal reaction at %(temp)s°C", temp=temperature)
        
        # ===== التعديل هنا: جلب الوصف من قاعدة البيانات =====
        cursor.execute("SELECT description FROM chemical_reactions WHERE id = ?", (reaction_id,))
        db_description = cursor.fetchone()
        
        if db_description and db_description[0]:
            # استخدام الوصف المخزن في قاعدة البيانات
            description = db_description[0]
        else:
            # استخدام الوصف من القاموس إذا لم يوجد وصف في قاعدة البيانات
            description = REACTION_DESCRIPTIONS.get(reaction_type, _("{} reaction occurred").format(reaction_type))
        # ===== انتهى التعديل =====
        
        # إضافة معلومات إضافية للوصف (اختياري - يمكنك حذف هذين السطرين إذا أردت)
        if precipitate:
            description += " with precipitate"
            result_text += " - Precipitate formed"
        if gas_produced:
            description += " with gas bubbles"
            result_text += " - Gas produced"
    else:
        # لا يوجد تفاعل محدد
        description = _("No predefined reaction found for %(r1)s and %(r2)s",
                r1=reactant1[1],
                r2=reactant2[1])
        temp_message ="ℹ️ " + _("Generic reaction at %(temp)s°C", temp=temperature)
        result_text =_("Generic reaction between %(r1)s and %(r2)s",
                r1=reactant1[1],
                r2=reactant2[1])

    # حفظ المحاكاة في جدول simulation (مع result و temperature)
    cursor.execute("""
        INSERT INTO simulation (user_id, reaction_id, date, result, temperature)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session["user_id"], 
        reaction_id if reaction_id else 0, 
        datetime.now(), 
        result_text or description,
        temperature
    ))

    simulation_id = cursor.lastrowid

    # حفظ نتيجة التفاعل في جدول reaction_results
    cursor.execute("""
        INSERT INTO reaction_results (simulation_id, products, state, color)
        VALUES (?, ?, ?, ?)
    """, (simulation_id, equation, reaction_type, result_color))

    db.commit()

    # تجهيز البيانات للعرض
    reaction_data = {
        'simulation_id': simulation_id,
        'reactant1_name': reactant1[1],
        'reactant2_name': reactant2[1],
        'reactant1_symbol': reactant1[2],
        'reactant2_symbol': reactant2[2],
        'reactant1_color': reactant1[3] or 'transparent',
        'reactant2_color': reactant2[3] or 'transparent',
        'quantity1': quantity1,
        'quantity2': quantity2,
        'equation': equation,
        'result_color': result_color,
        'description': description,
        'result_text': result_text,
        'reaction_type': reaction_type,
        'temperature': temperature,
        'gas_produced': gas_produced,
        'precipitate': precipitate,
        'pressure': pressure,
        'temp_message': temp_message,
        'has_reaction': reaction is not None
    }

    # جلب قائمة المتفاعلات لإعادة تعبئة القائمة في العمود الأيسر
    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements ORDER BY name")
    reactants = cursor.fetchall()
    reaction_data['reactants'] = reactants

    return render_template("simulation/simulation.html", **reaction_data)

    

@simulation_bp.route("/view/<int:simulation_id>", methods=["GET"])
def view_simulation(simulation_id):
    """عرض تفاصيل محاكاة محددة"""
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    
    db = get_db()
    cursor = db.cursor()
    
    # جلب بيانات المحاكاة من قاعدة البيانات
    cursor.execute("""
        SELECT 
            s.id, s.date, s.temperature, s.result,
            rr.products, rr.state, rr.color,
            r.gas_produced, r.precipitate,
            r.equation as reaction_equation,
            r.description as reaction_description
        FROM simulation s
        JOIN reaction_results rr ON s.id = rr.simulation_id
        LEFT JOIN chemical_reactions r ON s.reaction_id = r.id
        WHERE s.id = ? AND s.user_id = ?
    """, (simulation_id, session["user_id"]))
    
    sim = cursor.fetchone()
    
    if not sim:
        return "Simulation not found", 404
    
    # ===== التعديل هنا: استخدام الوصف من قاعدة البيانات =====
    # جلب الوصف من قاعدة البيانات إذا موجود
    db_description = sim[10] if len(sim) > 10 else None
    
    if db_description:
        final_description = db_description
    else:
        final_description = sim[3] or 'Reaction completed'
    # ===== انتهى التعديل =====
    
    # تجهيز البيانات للعرض
    reaction_data = {
        'simulation_id': sim[0],
        'date': sim[1],
        'temperature': sim[2] or 25,
        'result_text': sim[3] or '',
        'equation': sim[9] or sim[4] or 'Unknown Reaction',
        'result_color': sim[6] or 'transparent',
        'description': final_description,
        'reaction_type': sim[5] or 'unknown',
        'gas_produced': sim[7] or 0,
        'precipitate': sim[8] or 0,
        'reactant1_name': 'Reactant 1',
        'reactant2_name': 'Reactant 2',
        'reactant1_symbol': 'R1',
        'reactant2_symbol': 'R2',
        'reactant1_color': 'transparent',
        'reactant2_color': 'transparent',
        'quantity1': 1.0,
        'quantity2': 1.0
    }
    
    # إذا كان هناك معلومات إضافية في result_text
    if sim[3] and 'Gas' in sim[3]:
        reaction_data['gas_produced'] = 1
    if sim[3] and 'Precipitate' in sim[3]:
        reaction_data['precipitate'] = 1
    
    return render_template("simulation/simulation.html", **reaction_data)

@simulation_bp.route("/api/reaction/<int:simulation_id>", methods=["GET"])
def get_reaction_api(simulation_id):
    """API endpoint لجلب بيانات التفاعل (للجافاسكريبت)"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT s.id, s.user_id, s.reaction_id, s.date, s.result, s.temperature,
               rr.products, rr.state, rr.color
        FROM simulation s
        JOIN reaction_results rr ON s.id = rr.simulation_id
        WHERE s.id = ?
    """, (simulation_id,))
    
    result = cursor.fetchone()
    
    if result:
        data = {
            'id': result[0],
            'user_id': result[1],
            'reaction_id': result[2],
            'date': result[3],
            'result': result[4],
            'temperature': result[5],
            'equation': result[6],
            'reaction_type': result[7],
            'color': result[8]
        }
        return jsonify(data)
    
    return jsonify({'error': 'Simulation not found'}), 404

@simulation_bp.route("/history", methods=["GET"])
def simulation_history():
    """عرض تاريخ المحاكيات للمستخدم"""
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT s.id, s.date, s.result, s.temperature,
               rr.products, rr.color, rr.state,
               r.equation as reaction_equation
        FROM simulation s
        JOIN reaction_results rr ON s.id = rr.simulation_id
        LEFT JOIN chemical_reactions r ON s.reaction_id = r.id
        WHERE s.user_id = ?
        ORDER BY s.date DESC
        LIMIT 20
    """, (session["user_id"],))
    
    history = cursor.fetchall()
    
    return render_template("simulation/history.html", history=history)

@simulation_bp.route("/delete/<int:simulation_id>", methods=["POST"])
def delete_simulation(simulation_id):
    """حذف محاكاة محددة"""
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    
    db = get_db()
    cursor = db.cursor()
    
    # حذف من reaction_results أولاً (foreign key)
    cursor.execute("DELETE FROM reaction_results WHERE simulation_id = ?", (simulation_id,))
    
    # ثم حذف من simulation
    cursor.execute("DELETE FROM simulation WHERE id = ? AND user_id = ?", 
                  (simulation_id, session["user_id"]))
    
    db.commit()
    
    return redirect(url_for("simulation.simulation_history"))

@simulation_bp.route("/search", methods=["GET"])
def reactions_list():
    db = get_db()
    cursor = db.cursor()

    query = request.args.get("query")

    #  إذا البحث فارغ
    if not query or query.strip() == "":
        return render_template(
            "search/search.html",
            reactions=[],
             error="⚠️ " + _("Please enter a reaction to search.")
        )

    cursor.execute("""
        SELECT id, equation, type, result_color 
        FROM chemical_reactions
        WHERE equation LIKE ?
           OR type LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    reactions = cursor.fetchall()

    return render_template(
        "search/search.html",
        reactions=reactions,
        error=None
    )