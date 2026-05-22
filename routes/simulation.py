from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database.db import get_db
from datetime import datetime
import random
from flask import flash
from flask_babel import gettext as _


simulation_bp = Blueprint("simulation", __name__, url_prefix="/simulation")


REACTION_COLORS = {
    'neutralization': 'transparent',
    'precipitation': 'white',
    'complex': 'blue',
    'indicator': 'pink',
    'gas': 'bubbly',
    'default': 'transparent'
}

REACTION_DESCRIPTIONS = {
    'neutralization': 'Neutralization reaction completed - clear solution',
    'precipitation': 'Precipitate formed',
    'complex': 'Color changed to blue - complex formed',
    'indicator': 'Color changed to pink - indicator reaction',
    'gas': 'Gas bubbles released',
    'default': 'Reaction completed successfully'
}

@simulation_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in ['ar', 'en']:
        session['lang'] = lang
    # ارجع للصفحة التي جاء منها المستخدم
    return redirect(request.referrer or url_for("simulation.simulation_page"))


@simulation_bp.route("/", methods=["GET"])
def simulation_page():
    #   منع غير المسجل من دخول صفحة المحاكاة
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements ORDER BY name")
    reactants = cursor.fetchall()
    return render_template("simulation/simulation.html", reactants=reactants)


@simulation_bp.route('/start', methods=['GET', 'POST'])
def start_simulation():

    db = get_db()
    cursor = db.cursor()

    reactant1_id = request.form.get("reactant1")
    reactant2_id = request.form.get("reactant2")

    if not reactant1_id or not reactant2_id:
      return redirect(url_for("simulation.simulation_page"))

    if reactant1_id == reactant2_id:
        flash("⚠️ " + _("You cannot select the same reactant twice."), "error")
        return redirect(url_for("simulation.simulation_page"))

    quantity1 = float(request.form.get("quantity1", 0))
    quantity2 = float(request.form.get("quantity2", 0))
    temperature = float(request.form.get("temperature", 25))
    pressure_input = float(request.form.get("pressure", 1))

    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements WHERE id = ?", (reactant1_id,))
    reactant1 = cursor.fetchone()

    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements WHERE id = ?", (reactant2_id,))
    reactant2 = cursor.fetchone()

    gas_produced = 0
    precipitate = 0
    result_color = 'transparent'
    reaction_type = 'default'
    description = REACTION_DESCRIPTIONS['default']

    if not reactant1 or not reactant2:
        return "Error: Reactants not found", 404

    cursor.execute("""
    SELECT r.id, r.equation, r.type, r.result_color, r.gas_produced,
           r.precipitate, r.min_temp, r.temperature, r.pressure
    FROM chemical_reactions r
    WHERE r.id IN (
        SELECT re1.reaction_id
        FROM reaction_elements re1
        JOIN reaction_elements re2 
        ON re1.reaction_id = re2.reaction_id
        WHERE re1.element_id = ?
        AND re2.element_id = ?
    )
""", (reactant1_id, reactant2_id))

    reaction = cursor.fetchone()

    reaction_id = None
    equation = f"{reactant1[2]} + {reactant2[2]} → Product"

    min_temp = 20
    opt_temp = 25
    opt_pressure = 1.0
    min_pressure = 0.5
    pressure = pressure_input
    description = REACTION_DESCRIPTIONS['default']
    temp_message = ""
    result_text = ""

    if reaction:
        reaction_id, equation, reaction_type, result_color, gas_produced, precipitate, min_temp, temperature_db, pressure_db = reaction

        opt_pressure = pressure_db or 1.0
        min_pressure = max(0.5, opt_pressure - 1)
        opt_temp = temperature_db

        min_temp = min_temp or 20
        opt_temp = opt_temp or 25

        if temperature < min_temp:
            temp_message = _("⚠️ Temperature too low! Reaction needs at least %(temp)s°C", temp=min_temp)
            result_text = _("Slow reaction at %(temp)s°C", temp=temperature)
        elif temperature > opt_temp + 30:
            temp_message = _("⚠️ Temperature too high! Optimal temperature is %(temp)s°C", temp=opt_temp)
            result_text = _("Fast reaction at %(temp)s°C", temp=temperature)
        else:
            temp_message = _("✅ Optimal temperature (%(temp)s°C)", temp=temperature)
            result_text = _("Normal reaction at %(temp)s°C", temp=temperature)

        if pressure_input < min_pressure:
            temp_message += " " + _(
                "⚠️ Pressure too low! Recommended pressure is %(p)s atm",
                p=opt_pressure
            )
        elif pressure_input > (opt_pressure + 1):
            temp_message += " " + _(
                "⚠️ Pressure too high! Optimal pressure is %(p)s atm",
                p=opt_pressure
            )
        else:
            temp_message += " " + _(
                "✅ Suitable pressure (%(p)s atm)",
                p=pressure_input
            )

        cursor.execute("SELECT description FROM chemical_reactions WHERE id = ?", (reaction_id,))
        db_description = cursor.fetchone()

        if db_description and db_description[0]:
            description = db_description[0]
        else:
            description = REACTION_DESCRIPTIONS.get(reaction_type, _("{} reaction occurred").format(reaction_type))

        if precipitate:
            description += " with precipitate"
            result_text += " - Precipitate formed"
        if gas_produced:
            description += " with gas bubbles"
            result_text += " - Gas produced"

        cursor.execute("""
            INSERT INTO simulation (user_id, reaction_id, date, result, temperature, pressure)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session.get("user_id"),  # ممكن يكون None إذا لم يسجل دخول، نحتاج معالجة هذا
            reaction_id,
            datetime.now(),
            result_text or description,
            temperature,
            pressure_input
        ))

        simulation_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO reaction_results (simulation_id, products, state, color)
            VALUES (?, ?, ?, ?)
        """, (simulation_id, equation, reaction_type, result_color))

        db.commit()

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
            'pressure': pressure_input,
            'temp_message': temp_message,
            'has_reaction': True
        }

        cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements ORDER BY name")
        reactants = cursor.fetchall()
        reaction_data['reactants'] = reactants

        return render_template("simulation/simulation.html", **reaction_data)
    else:
        flash(_("❌ No reaction exists between %(r1)s and %(r2)s",
                r1=reactant1[1],
                r2=reactant2[1]), "error")
        return redirect(url_for("simulation.simulation_page"))
    
@simulation_bp.before_request
def change_lang_from_url():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')


@simulation_bp.route("/view/<int:simulation_id>", methods=["GET"])
def view_simulation(simulation_id):
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    
    db = get_db()
    cursor = db.cursor()
    
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
    
    db_description = sim[10] if len(sim) > 10 else None
    
    if db_description:
        final_description = db_description
    else:
        final_description = sim[3] or 'Reaction completed'
    
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
    
    if sim[3] and 'Gas' in sim[3]:
        reaction_data['gas_produced'] = 1
    if sim[3] and 'Precipitate' in sim[3]:
        reaction_data['precipitate'] = 1
        
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    
    return render_template("simulation/simulation.html", **reaction_data)


@simulation_bp.route("/api/reaction/<int:simulation_id>", methods=["GET"])
def get_reaction_api(simulation_id):
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
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM reaction_results WHERE simulation_id = ?", (simulation_id,))
    cursor.execute("DELETE FROM simulation WHERE id = ? AND user_id = ?", 
                  (simulation_id, session["user_id"]))
    
    db.commit()
    
    return redirect(url_for("simulation.simulation_history"))