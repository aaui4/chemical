import requests
from flask import Blueprint, render_template

compound_bp = Blueprint('compound', __name__)

@compound_bp.route('/encyclopedia')
def encyclopedia():
    compounds = [
        {"name": "Water", "formula": "H2O"},
        {"name": "Oxygen", "formula": "O2"},
        {"name": "Hydrogen", "formula": "H2"},
    ]
    return render_template("encyclopedia.html", compounds=compounds)

def get_description(name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/description/JSON"

    try:
        res = requests.get(url).json()
        return res["InformationList"]["Information"][0]["Description"]
    except:
        return None 
    
     

def get_compound_data(name):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight/JSON"
        res = requests.get(url).json()

        props = res["PropertyTable"]["Properties"][0]

        return {
            "formula": props.get("MolecularFormula"),
            "weight": props.get("MolecularWeight"),
            "description": get_description(name) or f"{name} is a chemical compound."
        }

    except:
        return {
            "formula": "N/A",
            "weight": "N/A",
            "description": "No data available."
        }


@compound_bp.route('/compound/<name>')
def compound_page(name):
    data = get_compound_data(name)

    return render_template("compound_page.html", compound={
        "name": name,
        "formula": data.get("formula"),
        "weight": data.get("weight"),
        "description": data.get("description"),
        "image": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/PNG"
    })

