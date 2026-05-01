import requests
from flask import Blueprint, render_template, request
from database.db import get_db

compound_bp = Blueprint('compound', __name__)

# ---------------- ENCYLOPEDIA ----------------
@compound_bp.route('/encyclopedia')
def encyclopedia():
    query = request.args.get("q")

    compounds = []
    reactions = []

    if query:
        comp = get_compound_data(query)
        if comp:
            compounds.append(comp)

        reactions = get_reactions(query)

    return render_template(
        "search/encyclopedia.html",
        compounds=compounds,
        reactions=reactions,
        query=query
    )

# ---------------- NORMALIZE INPUT ----------------
def normalize_formula(text):
    subscripts = {
        "₀": "0", "₁": "1", "₂": "2", "₃": "3",
        "₄": "4", "₅": "5", "₆": "6",
        "₇": "7", "₈": "8", "₉": "9"
    }

    for sub, normal in subscripts.items():
        text = text.replace(sub, normal)

    return text.strip()


# ---------------- PUBCHEM DESCRIPTION ----------------
def get_description(name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/description/JSON"

    try:
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return None

        data = res.json()

        info_list = data.get("InformationList", {}).get("Information", [])

        for item in info_list:
            desc = item.get("Description")
            if desc and len(desc) > 20:  # نتأكد description حقيقي
                return desc

        return None

    except Exception as e:
        print("ERROR DESC:", e)
        return None


# ---------------- GET CID (مهم للصورة) ----------------
def get_cid(name):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
        res = requests.get(url, timeout=5).json()
        return res["IdentifierList"]["CID"][0]
    except:
        return None


# ---------------- COMPOUND DATA ----------------
def get_compound_data(name):
    try:
        name = normalize_formula(name)

        # -------- properties --------
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight/JSON"
        res = requests.get(url, timeout=5).json()

        props = res["PropertyTable"]["Properties"][0]

        # -------- description --------
        desc = get_description(name)

        # -------- image via CID --------
        cid = get_cid(name)

        if cid:
            image = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
        else:
            image = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/PNG"

        return {
            "name": name,
            "formula": props.get("MolecularFormula", "N/A"),
            "weight": props.get("MolecularWeight", "N/A"),
            "description": desc if desc else f"No description found for {name}.",
            "image": image
        }

    except Exception as e:
        print("ERROR DATA:", e)
        return None


# ---------------- SINGLE PAGE ----------------
@compound_bp.route('/compound/<name>')
def compound_page(name):
    data = get_compound_data(name)

    if not data:
        data = {
            "name": name,
            "formula": "N/A",
            "weight": "N/A",
            "description": "No data available.",
            "image": None
        }

    return render_template("search/compound_page.html", compound=data)


# ---------------- REACTIONS FROM DB ----------------
def get_reactions(query):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM chemical_reactions
        WHERE equation LIKE ? OR description LIKE ? OR type LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))

    rows = cursor.fetchall()

    reactions = []

    for r in rows:
        reactions.append({
            "id": r["id"],
            "equation": r["equation"],
            "description": r["description"],
            "type": r["type"]
        })

    return reactions