import json
import importlib

try:
    chempy = importlib.import_module("chempy")
    balance_stoichiometry = chempy.balance_stoichiometry
except ImportError:
    balance_stoichiometry = None

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "database" / "reactions.json", "r", encoding="utf-8") as f:
    REACTIONS = json.load(f)



def normalize(x):
    return x.strip()


def predict_reaction(r1, r2):

    r1 = normalize(r1)
    r2 = normalize(r2)

    input_reactants = sorted([r1, r2])

    for reaction in REACTIONS:

        stored = sorted(reaction["reactants"])

        if stored == input_reactants:

            try:
                reac, prod = balance_stoichiometry(
                    set(reaction["reactants"]),
                    set(reaction["products"])
                )

                equation = " + ".join(reac.keys()) + " → " + " + ".join(prod.keys())

            except:
                equation = f"{r1} + {r2}"

            return {
                "equation": equation,
                "reaction_type": reaction["reaction_type"],
                "result_color": reaction["result_color"],
                "gas_produced": reaction["gas_produced"],
                "precipitate": reaction["precipitate"],
                "description": reaction["description"]
            }

    return {
        "equation": f"{r1} + {r2} → unknown",
        "reaction_type": "unknown",
        "result_color": "#999999",
        "gas_produced": 0,
        "precipitate": 0,
        "description": "No reaction found in dataset"
    }