from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database.db import get_db
from datetime import datetime
import random
from flask import flash
from flask_babel import gettext as _
import importlib
import json
import os

balance_stoichiometry = None
try:
    chempy = importlib.import_module("chempy")
    balance_stoichiometry = chempy.balance_stoichiometry
except ModuleNotFoundError:
    balance_stoichiometry = None


JSON_PATH = os.path.join("database", "reactions.json")

def load_json_reactants():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        reactants_dict = {}

        for reaction in data:
            for reactant in reaction.get("reactants", []):

                name = reactant.get("name", "")
                symbol = reactant.get("symbol", "")

                # المفتاح يكون الرمز الكيميائي
                if symbol not in reactants_dict:
                    reactants_dict[symbol] = {
                        "id": f"json_{symbol}",
                        "name": name,
                        "symbol": symbol,
                        "default_color": reactant.get("default_color", "#cccccc")
                    }

        return list(reactants_dict.values())

    except Exception as e:
        print("JSON load error:", e)
        return []

simulation_bp = Blueprint("simulation", __name__, url_prefix="/simulation")


REACTION_COLORS = {
    'neutralization': 'transparent',
    'precipitation': 'white',
    'complex': 'blue',
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

    if "user_id" not in session:
        return redirect(url_for("login.login"))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, name, symbol, default_color FROM chemical_elements ORDER BY name")
    db_reactants = cursor.fetchall()

    reactants = []
    for r in db_reactants:
        reactants.append({
            "id": r[0],
            "name": r[1],
            "symbol": r[2],
            "color": r[3] or "#ccc"
        })

    return render_template("simulation/simulation.html", reactants=reactants)


def get_reaction_from_json(symbol1, symbol2):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            reactions = json.load(f)

        for r in reactions:
            reactants = [
                x["symbol"].strip().upper()
                for x in r.get("reactants", [])
            ]

            if symbol1.upper() in reactants and symbol2.upper() in reactants:
                return r

    except Exception as e:
        print("JSON error:", e)

    return None
@simulation_bp.route('/start', methods=['POST'])
def start_simulation():

    db = get_db()
    cursor = db.cursor()

    # =========================
    # 1. قراءة الإدخال
    # =========================
    reactant1_id = request.form.get("reactant1")
    reactant2_id = request.form.get("reactant2")

    if not reactant1_id or not reactant2_id:
        return redirect(url_for("simulation.simulation_page"))

    reactant1_id = int(reactant1_id)
    reactant2_id = int(reactant2_id)

    if reactant1_id == reactant2_id:
        flash("⚠️ You cannot select the same reactant twice.", "error")
        return redirect(url_for("simulation.simulation_page"))

    quantity1 = float(request.form.get("quantity1", 0))
    quantity2 = float(request.form.get("quantity2", 0))
    temperature = float(request.form.get("temperature", 25))
    pressure_input = float(request.form.get("pressure", 1))

    # =========================
    # 2. جلب العناصر من DB
    # =========================
    cursor.execute("""
        SELECT id, name, symbol, default_color
        FROM chemical_elements
        WHERE id = ?
    """, (reactant1_id,))
    reactant1 = cursor.fetchone()

    cursor.execute("""
        SELECT id, name, symbol, default_color
        FROM chemical_elements
        WHERE id = ?
    """, (reactant2_id,))
    reactant2 = cursor.fetchone()

    if not reactant1 or not reactant2:
        return "Error: Reactants not found", 404

    # =========================
    # 3. جلب التفاعل من JSON
    # =========================
    json_reaction = get_reaction_from_json(
        reactant1[2],
        reactant2[2]
    )

    if json_reaction:
        equation = json_reaction.get("equation", "")
        reaction_type = json_reaction.get("type", "default")
        description = json_reaction.get("description", "")
        result_color = json_reaction.get("result_color", "transparent")
        gas_produced = json_reaction.get("gas_produced", 0)
        precipitate = json_reaction.get("precipitate", 0)
        opt_temp = json_reaction.get("temperature", 25)
        opt_pressure = json_reaction.get("pressure", 1)

    else:
        equation = f"{reactant1[2]} + {reactant2[2]} → ?"
        reaction_type = "default"
        description = "Reaction completed successfully"
        result_color = "transparent"
        gas_produced = 0
        precipitate = 0
        opt_temp = 25
        opt_pressure = 1

    # =========================
    # 4. تقييم الظروف (حرارة / ضغط)
    # =========================
    temp_message = ""

    if temperature < opt_temp:
        temp_message = f"⚠️ Temperature too low (optimal: {opt_temp}°C)"
    elif temperature > opt_temp + 30:
        temp_message = f"⚠️ Temperature too high (optimal: {opt_temp}°C)"
    else:
        temp_message = f"✅ Temperature OK ({temperature}°C)"

    if pressure_input < opt_pressure:
        temp_message += f" | ⚠️ Pressure too low (optimal: {opt_pressure} atm)"
    elif pressure_input > opt_pressure + 1:
        temp_message += f" | ⚠️ Pressure too high (optimal: {opt_pressure} atm)"
    else:
        temp_message += f" | ✅ Pressure OK ({pressure_input} atm)"

    # =========================
    # 5. حفظ المحاكاة
    # =========================
    cursor.execute("""
        INSERT INTO simulation
        (user_id, reaction_id, date, result, temperature, pressure)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session.get("user_id"),
        0,  # لأنك تعتمدين على JSON فقط
        datetime.now(),
        description,
        temperature,
        pressure_input
    ))

    simulation_id = cursor.lastrowid

    # =========================
    # 6. حفظ النتائج
    # =========================
    cursor.execute("""
        INSERT INTO reaction_results
        (simulation_id, products, state, color)
        VALUES (?, ?, ?, ?)
    """, (
        simulation_id,
        equation,
        reaction_type,
        result_color
    ))

    db.commit()

    # =========================
    # 7. عرض النتيجة
    # =========================
    return render_template(
        "simulation/simulation.html",
        simulation_id=simulation_id,
        reactant1_name=reactant1[1],
        reactant2_name=reactant2[1],
        reactant1_symbol=reactant1[2],
        reactant2_symbol=reactant2[2],
        equation=equation,
        description=description,
        reaction_type=reaction_type,
        result_color=result_color,
        temperature=temperature,
        pressure=pressure_input,
        gas_produced=gas_produced,
        precipitate=precipitate,
        quantity1=quantity1,
        quantity2=quantity2,
        has_reaction=True,
        temp_message=temp_message
    )

      
    
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