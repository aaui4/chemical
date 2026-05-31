import json
import sqlite3

DB_PATH = "chemical.db"
JSON_PATH = "reactions.json"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    reactions = json.load(f)

# =========================
# 1️⃣ إدخال العناصر
# =========================
for reaction in reactions:
    for r in reaction.get("reactants", []):

        name = r["name"]
        symbol = r["symbol"]
        color = r.get("default_color", "#ccc")
        state = r.get("state", "solid")

        cursor.execute("""
            INSERT OR IGNORE INTO chemical_elements
            (name, symbol, default_color, state)
            VALUES (?, ?, ?, ?)
        """, (name, symbol, color, state))

conn.commit()

# =========================
# 2️⃣ إدخال التفاعلات
# =========================
for reaction in reactions:

    equation = reaction["equation"]

    # check if reaction already exists
    cursor.execute("""
        SELECT id FROM chemical_reactions WHERE equation = ?
    """, (equation,))

    exists = cursor.fetchone()

    if exists:
        continue

    cursor.execute("""
        INSERT INTO chemical_reactions
        (equation, description, type, temperature, pressure,
         result_color, gas_produced, precipitate, min_temp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        equation,
        reaction.get("description", ""),
        reaction.get("type", "default"),
        reaction.get("temperature", 25),
        reaction.get("pressure", 1),
        reaction.get("result_color", "transparent"),
        reaction.get("gas_produced", 0),
        reaction.get("precipitate", 0),
        reaction.get("min_temp", 20)
    ))

    reaction_id = cursor.lastrowid

    # =========================
    # 3️⃣ ربط reactants
    # =========================
    for r in reaction.get("reactants", []):

        symbol = r["symbol"]

        cursor.execute("""
            SELECT id FROM chemical_elements WHERE symbol = ?
        """, (symbol,))

        row = cursor.fetchone()

        if row:
           cursor.execute("""
             SELECT 1 FROM reaction_elements
             WHERE reaction_id = ? AND element_id = ?
           """, (reaction_id, row[0]))

           exists = cursor.fetchone()

        if not exists:
             cursor.execute("""
                INSERT INTO reaction_elements (reaction_id, element_id)
                   VALUES (?, ?)
            """, (reaction_id, row[0]))

conn.commit()
conn.close()

print("✅ FULL IMPORT DONE (elements + reactions + links)")