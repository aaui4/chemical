import requests
from flask import Blueprint, render_template, request
from database.db import get_db

compound_bp = Blueprint('compound', __name__)

# ---------------- ENCYCLOPEDIA ----------------
@compound_bp.route('/encyclopedia')
def encyclopedia():
    query = request.args.get("q")

    compounds = []
    reactions = []
    q_type = None   #  مهم جدا

    if query:
        query = normalize_formula(query)
        q_type = detect_query_type(query)

        #  ELEMENT
        if q_type == "element":
            element = get_element_data(query)
            if element:
                compounds.append(element)

            compounds += search_compounds_by_symbol(query)

        #  COMPOUND
        elif q_type == "compound":
            comp = get_compound_data(query)
            if comp:
                compounds.append(comp)

            reactions = get_reactions(query)

        #  REACTION
        elif q_type == "reaction":
            reactions = get_reactions(query)

    return render_template(
        "search/encyclopedia.html",
        compounds=compounds,
        reactions=reactions,
        query=query
    )
    
# ---------------- DETECT TYPE ----------------
def detect_query_type(q):
    q = q.strip()

    if "+" in q or "→" in q or "=" in q:
        return "reaction"

    if len(q) <= 2 and q.isalpha():
        return "element"

    return "compound"

def get_element_data(symbol):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{symbol}/property/MolecularFormula,MolecularWeight/JSON"
        res = requests.get(url, timeout=5).json()

        props = res["PropertyTable"]["Properties"][0]

        return {
            "name": symbol,
            "formula": props.get("MolecularFormula", symbol),
            "weight": props.get("MolecularWeight", "N/A"),
            "description": f"{symbol} is a chemical element.",
            "image": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{symbol}/PNG"
        }

    except:
        return None
    
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

# ================ NEW FUNCTION: GET DETAILED COMPOUND INFO ================
def get_detailed_compound_info(name):
    """
    جلب معلومات مفصلة من PubChem وتنظيمها كالتالي:
    - Description
    - Uses
    - Properties
    - Safety
    """
    try:
        # الحصول على CID أولاً
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
        cid_res = requests.get(cid_url, timeout=5).json()
        
        if "IdentifierList" not in cid_res or "CID" not in cid_res["IdentifierList"]:
            return None
            
        cid = cid_res["IdentifierList"]["CID"][0]
        
        # جلب البيانات المفصلة من PUG View
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        res = requests.get(url, timeout=10).json()
        
        result = {
            "description": "",
            "uses": [],
            "properties": [],
            "safety": []
        }
        
        sections = res.get("Record", {}).get("Section", [])
        
        def extract_text_from_section(section):
            """استخراج النص من القسم"""
            texts = []
            for info in section.get("Information", []):
                val = info.get("Value", {})
                string_data = val.get("StringWithMarkup", [])
                if string_data:
                    text = string_data[0].get("String", "")
                    if text and len(text) > 20:
                        texts.append(text)
            return texts
        
        def search_sections(sec_list, depth=0):
            for sec in sec_list:
                title = sec.get("TOCHeading", "").lower()
                
                #  DESCRIPTION - الوصف العام
                if "description" in title or "summary" in title or "identification" in title:
                    texts = extract_text_from_section(sec)
                    if texts and not result["description"]:
                        result["description"] = texts[0][:1000]  # حد الطول
                
                #  USES - الاستخدامات
                if any(kw in title for kw in ["use", "application", "agricultural", "industrial", "pharmaceutical"]):
                    texts = extract_text_from_section(sec)
                    for text in texts:
                        if len(text) > 30 and text not in result["uses"]:
                            result["uses"].append(text[:500])
                
                #  PROPERTIES - الخواص
                if any(kw in title for kw in ["property", "physical", "chemical", "characteristic"]):
                    texts = extract_text_from_section(sec)
                    for text in texts:
                        if len(text) > 20 and text not in result["properties"]:
                            result["properties"].append(text[:300])
                
                #  SAFETY - الأمان والتحذيرات
                if any(kw in title for kw in ["safety", "hazard", "toxic", "warning", "precaution", "first aid"]):
                    texts = extract_text_from_section(sec)
                    for text in texts:
                        if len(text) > 20 and text not in result["safety"]:
                            result["safety"].append(text[:500])
                
                # البحث في الأقسام الفرعية
                if "Section" in sec:
                    search_sections(sec["Section"], depth + 1)
        
        search_sections(sections)
        
        # إذا لم نجد وصف، نستخدم وصفاً افتراضياً
        if not result["description"]:
            result["description"] = f"{name} is a chemical compound with various applications in industry and research."
        
        # إضافة بعض الخواص الأساسية من API البسيط
        try:
            prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight/MolecularFormula,MolecularWeight/JSON"
            prop_res = requests.get(prop_url, timeout=5).json()
            props = prop_res.get("PropertyTable", {}).get("Properties", [{}])[0]
            
            if props.get("MolecularFormula"):
                result["properties"].insert(0, f"Formula: {props['MolecularFormula']}")
            if props.get("MolecularWeight"):
                result["properties"].insert(1, f"Molecular Weight: {props['MolecularWeight']} g/mol")
        except:
            pass
        
        return result
        
    except Exception as e:
        print("DETAILED INFO ERROR:", e)
        return None

# ---------------- GET CID ----------------
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

        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight/JSON"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return None

        data = res.json()
        props_list = data.get("PropertyTable", {}).get("Properties", [])

        if not props_list:
            return None

        props = props_list[0]
        
        # جلب المعلومات المفصلة
        detailed_info = get_detailed_compound_info(name)

        #  صورة
        image = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/PNG"

        return {
            "name": name,
            "formula": props.get("MolecularFormula", "N/A"),
            "weight": props.get("MolecularWeight", "N/A"),
            "image": image,
            "detailed_info": detailed_info  # إضافة المعلومات المفصلة
        }

    except Exception as e:
        print("DATA ERROR:", e)
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
            "image": None,
            "detailed_info": None
        }

    return render_template("search/compound_page.html", compound=data)

# ---------------- REACTIONS FROM DB ----------------
def get_reactions(query):
    db = get_db()
    cursor = db.cursor()

    #  فلترة ذكية
    if len(query) <= 2:
        cursor.execute("""
            SELECT * FROM chemical_reactions
            WHERE equation LIKE ?
        """, (f"%{query}%",))
    else:
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

# ---------------- SEARCH BY SYMBOL ----------------
def search_compounds_by_symbol(symbol):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/formula/{symbol}/JSON"
        res = requests.get(url, timeout=5).json()

        compounds = []

        for c in res.get("PC_Compounds", [])[:10]:
            cid = c["id"]["id"]["cid"]

            try:
                name_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName,MolecularFormula/JSON"
                name_res = requests.get(name_url, timeout=5).json()

                props = name_res["PropertyTable"]["Properties"][0]

                name = props.get("IUPACName", f"Compound {cid}")
                formula = props.get("MolecularFormula", symbol)

            except:
                name = f"Compound {cid}"
                formula = symbol

            compounds.append({
                "name": name,
                "formula": formula,
                "cid": cid,
                "image": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
            })

        return compounds

    except Exception as e:
        print("ERROR SYMBOL:", e)
        return []